"""
Chronopoli Symposia – Step Functions Pipeline Client

Wrapper around boto3 Step Functions (SFN) for starting and managing
the post-session content pipeline that turns Round Table recordings
into transcripts, analysis papers, social posts, and partner reports.
"""

import json
import logging

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_sfn_client():
    """Return a boto3 Step Functions client configured from Django settings."""
    region = getattr(settings, "AWS_SFN_REGION", getattr(settings, "AWS_DEFAULT_REGION", "us-east-1"))
    return boto3.client("stepfunctions", region_name=region)


def start_pipeline(round_table_id, recording_s3_key):
    """
    Start the content-generation Step Functions pipeline for a Round Table.

    The state machine ARN is read from settings.SYMPOSIA_SFN_ARN.

    Args:
        round_table_id: Primary key of the RoundTable.
        recording_s3_key: S3 key of the session recording.

    Returns:
        The SFN execution ARN (str) on success, or None on failure.
    """
    client = _get_sfn_client()
    state_machine_arn = getattr(settings, "SYMPOSIA_SFN_ARN", "")

    if not state_machine_arn:
        logger.error("SYMPOSIA_SFN_ARN not configured in Django settings")
        return None

    pipeline_input = {
        "round_table_id": round_table_id,
        "recording_s3_key": recording_s3_key,
        "output_types": [
            "transcript",
            "analysis",
            "opinion_paper",
            "linkedin_post",
            "instagram_carousel",
            "video_script",
            "partner_report",
        ],
    }

    try:
        response = client.start_execution(
            stateMachineArn=state_machine_arn,
            name=f"rt-{round_table_id}-pipeline",
            input=json.dumps(pipeline_input),
        )

        execution_arn = response["executionArn"]
        logger.info(
            "Pipeline started for Round Table %s: %s",
            round_table_id,
            execution_arn,
        )
        return execution_arn

    except ClientError as exc:
        logger.error(
            "Failed to start pipeline for Round Table %s: %s",
            round_table_id,
            exc,
        )
        return None


def get_pipeline_status(execution_arn):
    """
    Get the current status of a Step Functions execution.

    Args:
        execution_arn: The ARN of the SFN execution.

    Returns:
        dict with keys: status, start_date, stop_date, output, error
        or None on failure.
    """
    client = _get_sfn_client()

    try:
        response = client.describe_execution(executionArn=execution_arn)
        return {
            "status": response["status"],
            "start_date": response.get("startDate"),
            "stop_date": response.get("stopDate"),
            "output": response.get("output"),
            "error": response.get("error"),
        }
    except ClientError as exc:
        logger.error("Failed to get pipeline status for %s: %s", execution_arn, exc)
        return None


def send_approval(task_token, approved):
    """
    Send an approval or rejection decision to a waiting Step Functions task.

    Used when the pipeline pauses at the human-approval step and a staff
    member approves or rejects the generated content.

    Args:
        task_token: The SFN task token from the approval callback.
        approved: True to approve, False to reject.

    Returns:
        True on success, False on failure.
    """
    client = _get_sfn_client()

    try:
        if approved:
            client.send_task_success(
                taskToken=task_token,
                output=json.dumps({"approved": True}),
            )
            logger.info("Pipeline approval sent (approved) for token %s...", task_token[:20])
        else:
            client.send_task_failure(
                taskToken=task_token,
                error="ContentRejected",
                cause="Staff member rejected the generated content.",
            )
            logger.info("Pipeline approval sent (rejected) for token %s...", task_token[:20])

        return True

    except ClientError as exc:
        logger.error("Failed to send pipeline approval for token %s: %s", task_token[:20], exc)
        return False
