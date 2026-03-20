"""
Chronopoli Symposia – Celery Tasks

Background tasks for polling the SQS approval queue and checking
pipeline execution status.
"""

import json
import logging

import boto3
from botocore.exceptions import ClientError
from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="chronopoli_symposia.poll_sqs_approval_queue")
def poll_sqs_approval_queue():
    """
    Poll the SQS queue for Step Functions approval callback messages.

    When the content pipeline reaches the human-approval step, SFN sends
    a message to SQS with the task token and output details. This task
    reads those messages, creates PipelineRun entries with status
    'waiting_approval', and makes the outputs available for staff review.
    """
    from .models import RoundTable, RoundTableOutput, PipelineRun

    queue_url = getattr(settings, "SYMPOSIA_APPROVAL_SQS_URL", "")
    if not queue_url:
        logger.debug("SYMPOSIA_APPROVAL_SQS_URL not configured, skipping poll")
        return

    region = getattr(settings, "AWS_SQS_REGION", getattr(settings, "AWS_DEFAULT_REGION", "us-east-1"))
    sqs = boto3.client("sqs", region_name=region)

    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5,
        )
    except ClientError as exc:
        logger.error("Failed to poll SQS approval queue: %s", exc)
        return

    messages = response.get("Messages", [])
    if not messages:
        logger.debug("No approval messages in queue")
        return

    for message in messages:
        try:
            body = json.loads(message["Body"])
            round_table_id = body.get("round_table_id")
            task_token = body.get("task_token")
            outputs = body.get("outputs", [])

            if not round_table_id or not task_token:
                logger.warning("Invalid SQS message body: %s", body)
                continue

            try:
                rt = RoundTable.objects.get(pk=round_table_id)
            except RoundTable.DoesNotExist:
                logger.warning("Round Table %s not found for approval message", round_table_id)
                continue

            # Update or create pipeline run
            pipeline_run, _ = PipelineRun.objects.update_or_create(
                round_table=rt,
                sfn_execution_arn=body.get("execution_arn", ""),
                defaults={"status": "waiting_approval"},
            )

            # Create output records
            now = timezone.now()
            for output_data in outputs:
                RoundTableOutput.objects.update_or_create(
                    round_table=rt,
                    output_type=output_data.get("output_type", "transcript"),
                    defaults={
                        "s3_key": output_data.get("s3_key", ""),
                        "content_preview": output_data.get("preview", "")[:500],
                        "status": "generated",
                        "generated_at": now,
                    },
                )

            logger.info(
                "Processed approval message for Round Table %s (%d outputs)",
                rt.slug,
                len(outputs),
            )

            # Delete processed message from queue
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message["ReceiptHandle"],
            )

        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Failed to process SQS message: %s", exc)


@shared_task(name="chronopoli_symposia.check_pipeline_status")
def check_pipeline_status(pipeline_run_id):
    """
    Check the current status of a Step Functions pipeline execution
    and update the PipelineRun model accordingly.

    Args:
        pipeline_run_id: Primary key of the PipelineRun to check.
    """
    from .models import PipelineRun
    from .pipeline import get_pipeline_status

    try:
        run = PipelineRun.objects.select_related("round_table").get(pk=pipeline_run_id)
    except PipelineRun.DoesNotExist:
        logger.warning("PipelineRun %s not found", pipeline_run_id)
        return

    result = get_pipeline_status(run.sfn_execution_arn)
    if result is None:
        logger.warning("Could not get status for PipelineRun %s", pipeline_run_id)
        return

    sfn_status = result["status"]

    if sfn_status == "SUCCEEDED":
        run.status = "completed"
        run.completed_at = timezone.now()
        run.round_table.status = "completed"
        run.round_table.save(update_fields=["status"])
    elif sfn_status == "FAILED":
        run.status = "failed"
        run.error_message = result.get("error", "Unknown error")
        run.completed_at = timezone.now()
    elif sfn_status == "RUNNING":
        run.status = "running"
    # ABORTED or other states
    else:
        run.status = "failed"
        run.error_message = f"Unexpected SFN status: {sfn_status}"
        run.completed_at = timezone.now()

    run.save()
    logger.info("PipelineRun %s updated to status: %s", pipeline_run_id, run.status)
