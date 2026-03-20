"""
Chronopoli Symposia Pipeline – Step 1: Start Transcription
Submits an AWS Transcribe job for a round table recording.
"""

import json
import logging
import os
import time
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

S3_BUCKET_OUTPUTS = os.environ["S3_BUCKET_OUTPUTS"]
AWS_REGION = os.environ.get("AWS_REGION", "me-central-1")

transcribe = boto3.client("transcribe", region_name=AWS_REGION)


def handler(event, context):
    """
    Receives:
        {"recording_s3_uri": "s3://bucket/key.mp4", "round_table_id": "123"}
    Returns:
        {"job_name": "chronopoli-rt-123-<ts>", "round_table_id": "123"}
    """
    try:
        recording_s3_uri = event["recording_s3_uri"]
        round_table_id = str(event["round_table_id"])

        timestamp = int(time.time())
        job_name = f"chronopoli-rt-{round_table_id}-{timestamp}"

        logger.info(
            "Starting transcription job %s for round table %s",
            job_name,
            round_table_id,
        )

        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": recording_s3_uri},
            MediaFormat=_detect_format(recording_s3_uri),
            LanguageCode="en-US",
            OutputBucketName=S3_BUCKET_OUTPUTS,
            OutputKey=f"transcripts/{round_table_id}/{job_name}.json",
            Settings={
                "ShowSpeakerLabels": True,
                "MaxSpeakerLabels": 20,
            },
        )

        logger.info("Transcription job %s submitted successfully", job_name)

        return {
            "job_name": job_name,
            "round_table_id": round_table_id,
        }

    except Exception:
        logger.exception("Failed to start transcription job")
        raise


def _detect_format(s3_uri: str) -> str:
    """Detect media format from S3 URI extension."""
    lower = s3_uri.lower()
    if lower.endswith(".mp4"):
        return "mp4"
    if lower.endswith(".webm"):
        return "webm"
    if lower.endswith(".flac"):
        return "flac"
    if lower.endswith(".wav"):
        return "wav"
    return "mp4"
