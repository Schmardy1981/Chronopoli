"""
Chronopoli Symposia Pipeline – Step 3: Analyze Transcript with Claude
Calls Amazon Bedrock (Claude) to extract structured analysis from transcript.
"""

import json
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

S3_BUCKET_OUTPUTS = os.environ["S3_BUCKET_OUTPUTS"]
AWS_REGION = os.environ.get("AWS_REGION", "me-central-1")

s3 = boto3.client("s3", region_name=AWS_REGION)
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

ANALYSIS_PROMPT = """You are an expert analyst for Chronopoli, a global knowledge platform
covering AI, blockchain, governance, compliance, financial crime investigation, and enterprise risk.

Analyze the following round table discussion transcript and extract a structured analysis.

Return ONLY valid JSON with these exact keys:
{
  "title": "A concise, descriptive title for this round table discussion",
  "executive_summary": "2-3 paragraph executive summary of the discussion",
  "core_theses": ["List of 3-6 core theses or arguments presented"],
  "key_disagreements": ["List of notable disagreements or debates between participants"],
  "consensus_points": ["List of points where participants broadly agreed"],
  "key_quotes": [
    {"speaker": "Name", "quote": "Exact or near-exact quote", "context": "Brief context"}
  ],
  "recommendations": ["List of actionable recommendations that emerged"],
  "participants_mentioned": [
    {"name": "Full Name", "organization": "Company/Org", "role": "Title if mentioned"}
  ],
  "topics_covered": ["List of main topics/themes"],
  "district_relevance": {
    "CHRON-AI": 0.0,
    "CHRON-DA": 0.0,
    "CHRON-GOV": 0.0,
    "CHRON-COMP": 0.0,
    "CHRON-INV": 0.0,
    "CHRON-RISK": 0.0
  }
}

For district_relevance, score each district 0.0-1.0 based on how relevant the discussion is.

TRANSCRIPT:
{transcript}
"""


def handler(event, context):
    """
    Receives:
        {"transcript_text": "...", "round_table_id": "123"}
    Returns:
        {"analysis": {...}, "round_table_id": "123"}
    """
    try:
        transcript_text = event["transcript_text"]
        round_table_id = str(event["round_table_id"])

        logger.info(
            "Analyzing transcript for round table %s (%d chars)",
            round_table_id,
            len(transcript_text),
        )

        # Truncate very long transcripts to fit context window
        max_chars = 180_000
        if len(transcript_text) > max_chars:
            logger.warning(
                "Transcript truncated from %d to %d chars",
                len(transcript_text),
                max_chars,
            )
            transcript_text = transcript_text[:max_chars]

        prompt = ANALYSIS_PROMPT.format(transcript=transcript_text)

        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 8192,
                "temperature": 0.2,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            }),
        )

        response_body = json.loads(response["body"].read())
        raw_text = response_body["content"][0]["text"]

        # Parse JSON from Claude response (handle markdown fences)
        analysis = _extract_json(raw_text)

        # Save analysis to S3
        s3_key = f"outputs/{round_table_id}/analysis.json"
        s3.put_object(
            Bucket=S3_BUCKET_OUTPUTS,
            Key=s3_key,
            Body=json.dumps(analysis, indent=2),
            ContentType="application/json",
        )
        logger.info("Analysis saved to s3://%s/%s", S3_BUCKET_OUTPUTS, s3_key)

        return {
            "analysis": analysis,
            "round_table_id": round_table_id,
        }

    except Exception:
        logger.exception("Failed to analyze transcript")
        raise


def _extract_json(text: str) -> dict:
    """Extract JSON from text, handling markdown code fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = cleaned.index("\n")
        cleaned = cleaned[first_newline + 1:]
        # Remove closing fence
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return json.loads(cleaned)
