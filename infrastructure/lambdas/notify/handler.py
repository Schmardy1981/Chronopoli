"""
Chronopoli Symposia Pipeline – Step 6: Notify Staff for Approval
Sends SQS message to Django approval queue and SES email to staff.
"""

import json
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

S3_BUCKET_OUTPUTS = os.environ["S3_BUCKET_OUTPUTS"]
AWS_REGION = os.environ.get("AWS_REGION", "me-central-1")
SQS_APPROVAL_QUEUE_URL = os.environ["SQS_APPROVAL_QUEUE_URL"]
STAFF_EMAIL = os.environ["STAFF_EMAIL"]

sqs = boto3.client("sqs", region_name=AWS_REGION)
ses = boto3.client("ses", region_name=AWS_REGION)


def handler(event, context):
    """
    Receives:
        {
            "round_table_id": "123",
            "opinion_paper_key": "outputs/123/opinion_paper.pdf",
            "linkedin_key": "outputs/123/linkedin_post.json",
            "instagram_key": "outputs/123/instagram_carousel.json",
            "partner_reports_key": "outputs/123/partner_reports.json",
            "analysis_key": "outputs/123/analysis.json"
        }
    Returns:
        {"notified": true}
    """
    try:
        round_table_id = str(event["round_table_id"])

        output_keys = {
            "opinion_paper": event.get("opinion_paper_key", ""),
            "linkedin_post": event.get("linkedin_key", ""),
            "instagram_carousel": event.get("instagram_key", ""),
            "partner_reports": event.get("partner_reports_key", ""),
            "analysis": event.get("analysis_key", ""),
        }

        logger.info(
            "Notifying staff for round table %s approval", round_table_id
        )

        # 1. Send SQS message for Django approval workflow
        sqs_message = {
            "round_table_id": round_table_id,
            "bucket": S3_BUCKET_OUTPUTS,
            "outputs": output_keys,
            "status": "pending_approval",
        }

        sqs.send_message(
            QueueUrl=SQS_APPROVAL_QUEUE_URL,
            MessageBody=json.dumps(sqs_message),
            MessageAttributes={
                "round_table_id": {
                    "DataType": "String",
                    "StringValue": round_table_id,
                },
                "event_type": {
                    "DataType": "String",
                    "StringValue": "symposia_outputs_ready",
                },
            },
        )
        logger.info("SQS approval message sent for round table %s", round_table_id)

        # 2. Send SES notification email to staff
        s3_console_prefix = (
            f"https://s3.console.aws.amazon.com/s3/buckets/"
            f"{S3_BUCKET_OUTPUTS}?prefix=outputs/{round_table_id}/"
        )

        email_body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #0D0D0D; color: #E5E5E5; padding: 20px;">
          <div style="max-width: 600px; margin: auto;">
            <h1 style="color: #C9A84C;">Chronopoli Symposia</h1>
            <h2 style="color: #FFFFFF;">Round Table #{round_table_id} – Outputs Ready</h2>
            <p>The AI pipeline has finished processing this round table recording.
               The following outputs are ready for your review and approval:</p>
            <ul>
              <li>Opinion Paper (PDF)</li>
              <li>LinkedIn Post Draft</li>
              <li>Instagram Carousel Content</li>
              <li>Partner Intelligence Reports</li>
            </ul>
            <p><a href="{s3_console_prefix}"
                  style="color: #C9A84C;">View outputs in S3 Console</a></p>
            <p style="color: #888; font-size: 12px;">
              This is an automated notification from the Chronopoli Symposia pipeline.
              Please review and approve outputs before publication.
            </p>
          </div>
        </body>
        </html>
        """

        ses.send_email(
            Source=f"Chronopoli Symposia <noreply@chronopoli.io>",
            Destination={"ToAddresses": [STAFF_EMAIL]},
            Message={
                "Subject": {
                    "Data": f"[Chronopoli] Round Table #{round_table_id} outputs ready for review",
                },
                "Body": {
                    "Html": {"Data": email_body_html},
                    "Text": {
                        "Data": (
                            f"Round Table #{round_table_id} outputs are ready.\n"
                            f"Review in S3: {s3_console_prefix}\n"
                            f"Outputs: opinion paper, LinkedIn post, "
                            f"Instagram carousel, partner reports."
                        ),
                    },
                },
            },
        )
        logger.info("SES notification sent to %s", STAFF_EMAIL)

        return {"notified": True}

    except Exception:
        logger.exception("Failed to send notifications")
        raise
