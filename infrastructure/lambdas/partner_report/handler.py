"""
Chronopoli Symposia Pipeline – Step 5c: Generate Partner Reports
Analyzes sentiment, competitor mentions, and recommendations per partner.
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

PARTNER_PROMPT = """You are a business intelligence analyst for Chronopoli, a global knowledge platform
hosted by Dubai Blockchain Center.

Given the round table analysis below, generate a report for EACH company/organization
mentioned in participants_mentioned. For each organization, provide:

1. Sentiment analysis: How was the organization discussed? (positive/neutral/negative + explanation)
2. Competitor mentions: Were any competitors to this organization mentioned? What was said?
3. Market positioning: How does this organization's position appear based on discussion?
4. Recommended actions: What should Chronopoli's partnership team do regarding this organization?

Return ONLY valid JSON:
{{
  "partner_reports": [
    {{
      "organization": "Company Name",
      "representative": "Person Name",
      "sentiment": "positive|neutral|negative|mixed",
      "sentiment_explanation": "Why this sentiment rating",
      "competitor_mentions": [
        {{"competitor": "Name", "context": "What was said"}}
      ],
      "market_positioning": "Brief assessment of their positioning",
      "recommended_actions": ["Action 1", "Action 2"],
      "partnership_opportunity_score": 0.0
    }}
  ],
  "overall_industry_sentiment": "Brief overall market sentiment from discussion"
}}

partnership_opportunity_score: 0.0-1.0 (how strong the partnership opportunity is for Chronopoli).

ANALYSIS:
{analysis_json}
"""


def handler(event, context):
    """
    Receives:
        {"analysis": {...}, "round_table_id": "123"}
    Returns:
        {"s3_key": "outputs/123/partner_reports.json", "partners_count": N}
    """
    try:
        analysis = event["analysis"]
        round_table_id = str(event["round_table_id"])

        participants = analysis.get("participants_mentioned", [])
        logger.info(
            "Generating partner reports for round table %s (%d participants)",
            round_table_id,
            len(participants),
        )

        if not participants:
            # No participants to analyze
            empty_report = {
                "partner_reports": [],
                "overall_industry_sentiment": "No participants identified.",
            }
            s3_key = f"outputs/{round_table_id}/partner_reports.json"
            s3.put_object(
                Bucket=S3_BUCKET_OUTPUTS,
                Key=s3_key,
                Body=json.dumps(empty_report, indent=2),
                ContentType="application/json",
            )
            return {"s3_key": s3_key, "partners_count": 0}

        prompt = PARTNER_PROMPT.format(
            analysis_json=json.dumps(analysis, indent=2)
        )

        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.3,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            }),
        )

        response_body = json.loads(response["body"].read())
        raw_text = response_body["content"][0]["text"]
        partner_data = _extract_json(raw_text)

        s3_key = f"outputs/{round_table_id}/partner_reports.json"
        s3.put_object(
            Bucket=S3_BUCKET_OUTPUTS,
            Key=s3_key,
            Body=json.dumps(partner_data, indent=2),
            ContentType="application/json",
        )

        partners_count = len(partner_data.get("partner_reports", []))
        logger.info(
            "Partner reports saved to s3://%s/%s (%d partners)",
            S3_BUCKET_OUTPUTS,
            s3_key,
            partners_count,
        )

        return {"s3_key": s3_key, "partners_count": partners_count}

    except Exception:
        logger.exception("Failed to generate partner reports")
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
