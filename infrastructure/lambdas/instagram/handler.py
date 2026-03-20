"""
Chronopoli Symposia Pipeline – Step 5b: Generate Instagram Carousel
Calls Bedrock Claude to produce carousel slide content + image keywords.
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

INSTAGRAM_PROMPT = """You are a social media designer for Chronopoli, a global knowledge platform
hosted by Dubai Blockchain Center. Brand colors: dark backgrounds (#0D0D0D), gold accents (#C9A84C).

Based on the following round table analysis, create an Instagram carousel post (5-8 slides).

Requirements per slide:
- Slide 1: Bold title card with the round table topic
- Slides 2-6: One key insight per slide (short punchy text, max 30 words per slide)
- Second-to-last slide: A compelling quote from a participant
- Last slide: CTA – "Learn more at chronopoli.io" or "Join the conversation"
- For each slide, suggest image keywords for AI image generation

Return ONLY valid JSON:
{{
  "caption": "Instagram caption text with emojis and hashtags (max 2200 chars)",
  "slides": [
    {{
      "slide_number": 1,
      "headline": "Short headline",
      "body_text": "Text for the slide (max 30 words)",
      "image_keywords": ["keyword1", "keyword2", "keyword3"],
      "text_color": "#FFFFFF or #C9A84C"
    }}
  ],
  "hashtags": ["#tag1", "#tag2"]
}}

ANALYSIS:
{analysis_json}
"""


def handler(event, context):
    """
    Receives:
        {"analysis": {...}, "round_table_id": "123"}
    Returns:
        {"s3_key": "outputs/123/instagram_carousel.json"}
    """
    try:
        analysis = event["analysis"]
        round_table_id = str(event["round_table_id"])

        logger.info(
            "Generating Instagram carousel for round table %s", round_table_id
        )

        prompt = INSTAGRAM_PROMPT.format(
            analysis_json=json.dumps(analysis, indent=2)
        )

        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.7,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            }),
        )

        response_body = json.loads(response["body"].read())
        raw_text = response_body["content"][0]["text"]
        carousel_data = _extract_json(raw_text)

        s3_key = f"outputs/{round_table_id}/instagram_carousel.json"
        s3.put_object(
            Bucket=S3_BUCKET_OUTPUTS,
            Key=s3_key,
            Body=json.dumps(carousel_data, indent=2),
            ContentType="application/json",
        )
        logger.info(
            "Instagram carousel saved to s3://%s/%s (%d slides)",
            S3_BUCKET_OUTPUTS,
            s3_key,
            len(carousel_data.get("slides", [])),
        )

        return {"s3_key": s3_key}

    except Exception:
        logger.exception("Failed to generate Instagram carousel")
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
