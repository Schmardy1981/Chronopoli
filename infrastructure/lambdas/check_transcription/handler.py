"""
Chronopoli Symposia Pipeline – Step 2: Check Transcription Status
Polls AWS Transcribe job and fetches transcript when complete.
"""

import json
import logging
import os
import urllib.parse
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_REGION = os.environ.get("AWS_REGION", "me-central-1")

transcribe = boto3.client("transcribe", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)


def handler(event, context):
    """
    Receives:
        {"job_name": "chronopoli-rt-123-...", "round_table_id": "123"}
    Returns:
        {"status": "COMPLETED"|"IN_PROGRESS"|"FAILED",
         "transcript_text": "...",        # only when COMPLETED
         "transcript_s3_key": "...",       # only when COMPLETED
         "job_name": "...",
         "round_table_id": "..."}
    """
    try:
        job_name = event["job_name"]
        round_table_id = str(event.get("round_table_id", ""))

        logger.info("Checking transcription job %s", job_name)

        response = transcribe.get_transcription_job(
            TranscriptionJobName=job_name
        )
        job = response["TranscriptionJob"]
        status = job["TranscriptionJobStatus"]

        result = {
            "status": status,
            "job_name": job_name,
            "round_table_id": round_table_id,
        }

        if status == "COMPLETED":
            transcript_uri = job["Transcript"]["TranscriptFileUri"]
            bucket, key = _parse_s3_uri(transcript_uri)

            logger.info("Fetching transcript from s3://%s/%s", bucket, key)
            obj = s3.get_object(Bucket=bucket, Key=key)
            transcript_data = json.loads(obj["Body"].read().decode("utf-8"))

            transcript_text = transcript_data["results"]["transcripts"][0][
                "transcript"
            ]

            result["transcript_text"] = transcript_text
            result["transcript_s3_key"] = key
            logger.info(
                "Transcript fetched, length=%d chars", len(transcript_text)
            )

        elif status == "FAILED":
            failure_reason = job.get("FailureReason", "Unknown")
            logger.error("Transcription failed: %s", failure_reason)
            result["failure_reason"] = failure_reason

        else:
            logger.info("Transcription still in progress")

        return result

    except Exception:
        logger.exception("Failed to check transcription job")
        raise


def _parse_s3_uri(uri: str) -> tuple:
    """Parse an S3 URI or HTTPS URL into (bucket, key)."""
    if uri.startswith("s3://"):
        parts = uri[5:].split("/", 1)
        return parts[0], parts[1]
    # Transcribe returns HTTPS URLs
    parsed = urllib.parse.urlparse(uri)
    # https://s3.<region>.amazonaws.com/<bucket>/<key>
    path_parts = parsed.path.lstrip("/").split("/", 1)
    return path_parts[0], path_parts[1]
