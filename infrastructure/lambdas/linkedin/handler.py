"""
Chronopoli Symposia Pipeline – Step 5a: Generate LinkedIn Post
Calls Bedrock Claude to produce a LinkedIn post for Chronopoli's page.
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

LINKEDIN_PROMPT = """You are a social media strategist for Chronopoli, a global knowledge platform
hosted by Dubai Blockchain Center. Chronopoli covers AI, blockchain, governance, compliance,
financial crime investigation, and enterprise risk.

Based on the following round table analysis, write ONE LinkedIn post for the Chronopoli company page.

Requirements:
- Professional, authoritative tone
- 150-250 words
- Start with a compelling hook (no hashtags in first line)
- Include 2-3 key takeaways as bullet points
- End with a call to action (visit chronopoli.io or join the next round table)
- Include 5-8 relevant hashtags at the end
- Mention notable participants by name if appropriate

Return ONLY valid JSON:
{{
  "post_text": "The full LinkedIn post text",
  "headline": "A short headline for internal reference",
  "hashtags": ["#tag1", "#tag2"],
  "mentioned_people": ["Name1", "Name2"]
}}

ANALYSIS:
{analysis_json}
"""


def handler(event, context):
    """
    Receives:
        {"analysis": {...}, "round_table_id": "123"}
    Returns:
        {"s3_key": "outputs/123/linkedin_post.json"}
    """
    try:
        analysis = event["analysis"]
        round_table_id = str(event["round_table_id"])

        logger.info("Generating LinkedIn post for round table %s", round_table_id)

        prompt = LINKEDIN_PROMPT.format(
            analysis_json=json.dumps(analysis, indent=2)
        )

        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "temperature": 0.7,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            }),
        )

        response_body = json.loads(response["body"].read())
        raw_text = response_body["content"][0]["text"]
        linkedin_data = _extract_json(raw_text)

        s3_key = f"outputs/{round_table_id}/linkedin_post.json"
        s3.put_object(
            Bucket=S3_BUCKET_OUTPUTS,
            Key=s3_key,
            Body=json.dumps(linkedin_data, indent=2),
            ContentType="application/json",
        )
        logger.info("LinkedIn post saved to s3://%s/%s", S3_BUCKET_OUTPUTS, s3_key)

        return {"s3_key": s3_key}

    except Exception:
        logger.exception("Failed to generate LinkedIn post")
        raise


def _extract_json(text: str) -> dict:
    """Extract JSON from text, handling markdown code fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.index("\n")
        cleaned = cleaned[first_newline + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return json.loads(cleaned)
