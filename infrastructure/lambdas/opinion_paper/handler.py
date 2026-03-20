"""
Chronopoli Symposia Pipeline – Step 4: Generate Opinion Paper (PDF)
Renders a branded HTML opinion paper from analysis and converts to PDF.
"""

import json
import logging
import os
import boto3
from jinja2 import Template
from weasyprint import HTML

logger = logging.getLogger()
logger.setLevel(logging.INFO)

S3_BUCKET_OUTPUTS = os.environ["S3_BUCKET_OUTPUTS"]
AWS_REGION = os.environ.get("AWS_REGION", "me-central-1")

s3 = boto3.client("s3", region_name=AWS_REGION)

DISTRICT_NAMES = {
    "CHRON-AI": "AI District",
    "CHRON-DA": "Digital Assets District",
    "CHRON-GOV": "Governance District",
    "CHRON-COMP": "Compliance District",
    "CHRON-INV": "Investigation District",
    "CHRON-RISK": "Risk & Trust District",
}

OPINION_PAPER_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{{ title }} – Chronopoli Opinion Paper</title>
<style>
  @page {
    size: A4;
    margin: 2cm 2.5cm;
    @bottom-center {
      content: "Chronopoli – Global Knowledge City | Page " counter(page) " of " counter(pages);
      font-size: 8pt;
      color: #888;
    }
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background: #0D0D0D;
    color: #E5E5E5;
    font-size: 11pt;
    line-height: 1.6;
  }
  .cover {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    text-align: center;
    padding: 4cm 2cm;
  }
  .cover .logo-text {
    font-size: 36pt;
    font-weight: 700;
    letter-spacing: 6px;
    color: #C9A84C;
    text-transform: uppercase;
    margin-bottom: 0.5cm;
  }
  .cover .subtitle {
    font-size: 12pt;
    color: #888;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 2cm;
  }
  .cover .paper-title {
    font-size: 24pt;
    font-weight: 600;
    color: #FFFFFF;
    max-width: 80%;
    margin-bottom: 1cm;
  }
  .cover .districts {
    display: flex;
    gap: 0.5cm;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 1.5cm;
  }
  .cover .district-badge {
    background: rgba(201, 168, 76, 0.15);
    border: 1px solid #C9A84C;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 9pt;
    color: #C9A84C;
    letter-spacing: 1px;
  }
  .cover .date {
    font-size: 10pt;
    color: #666;
  }
  .section {
    margin-bottom: 1.2cm;
  }
  h2 {
    font-size: 16pt;
    font-weight: 600;
    color: #C9A84C;
    border-bottom: 2px solid #C9A84C;
    padding-bottom: 4px;
    margin-bottom: 0.5cm;
  }
  h3 {
    font-size: 12pt;
    font-weight: 600;
    color: #FFFFFF;
    margin-bottom: 0.3cm;
  }
  p { margin-bottom: 0.4cm; }
  ul {
    margin-left: 0.6cm;
    margin-bottom: 0.4cm;
  }
  li { margin-bottom: 0.2cm; }
  .quote-block {
    border-left: 3px solid #C9A84C;
    padding: 0.3cm 0.5cm;
    margin: 0.4cm 0;
    background: rgba(201, 168, 76, 0.05);
  }
  .quote-block .speaker {
    font-weight: 600;
    color: #C9A84C;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .quote-block .text {
    font-style: italic;
    color: #CCC;
  }
  .divider {
    border: none;
    border-top: 1px solid #333;
    margin: 0.8cm 0;
  }
  .disclaimer {
    font-size: 8pt;
    color: #666;
    border-top: 1px solid #333;
    padding-top: 0.3cm;
    margin-top: 1cm;
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <div class="logo-text">CHRONOPOLI</div>
  <div class="subtitle">Global Knowledge City &bull; Dubai Blockchain Center</div>
  <div class="paper-title">{{ title }}</div>
  <div class="districts">
    {% for code in district_codes %}
    <span class="district-badge">{{ district_names.get(code, code) }}</span>
    {% endfor %}
  </div>
  <div class="date">Opinion Paper &bull; Round Table #{{ round_table_id }}</div>
</div>

<!-- EXECUTIVE SUMMARY -->
<div class="section">
  <h2>Executive Summary</h2>
  <p>{{ executive_summary }}</p>
</div>

<!-- CORE THESES -->
<div class="section">
  <h2>Core Theses</h2>
  <ul>
    {% for thesis in core_theses %}
    <li>{{ thesis }}</li>
    {% endfor %}
  </ul>
</div>

<!-- CONSENSUS POINTS -->
{% if consensus_points %}
<div class="section">
  <h2>Areas of Consensus</h2>
  <ul>
    {% for point in consensus_points %}
    <li>{{ point }}</li>
    {% endfor %}
  </ul>
</div>
{% endif %}

<!-- KEY DISAGREEMENTS -->
{% if key_disagreements %}
<div class="section">
  <h2>Key Disagreements</h2>
  <ul>
    {% for item in key_disagreements %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
</div>
{% endif %}

<hr class="divider">

<!-- KEY QUOTES -->
{% if key_quotes %}
<div class="section">
  <h2>Notable Quotes</h2>
  {% for q in key_quotes %}
  <div class="quote-block">
    <div class="speaker">{{ q.speaker }}</div>
    <div class="text">&ldquo;{{ q.quote }}&rdquo;</div>
  </div>
  {% endfor %}
</div>
{% endif %}

<!-- RECOMMENDATIONS -->
{% if recommendations %}
<div class="section">
  <h2>Recommendations</h2>
  <ul>
    {% for rec in recommendations %}
    <li>{{ rec }}</li>
    {% endfor %}
  </ul>
</div>
{% endif %}

<!-- PARTICIPANTS -->
{% if participants_mentioned %}
<div class="section">
  <h2>Participants</h2>
  <ul>
    {% for p in participants_mentioned %}
    <li><strong>{{ p.name }}</strong>{% if p.organization %}, {{ p.organization }}{% endif %}{% if p.role %} ({{ p.role }}){% endif %}</li>
    {% endfor %}
  </ul>
</div>
{% endif %}

<div class="disclaimer">
  This opinion paper was generated by Chronopoli's AI-assisted Symposia pipeline
  from a recorded round table discussion. Content has been reviewed for accuracy
  but may not represent the official positions of participants or their organizations.
  &copy; Chronopoli / Dubai Blockchain Center. All rights reserved.
</div>

</body>
</html>
""")


def handler(event, context):
    """
    Receives:
        {"analysis": {...}, "round_table_id": "123", "district_codes": [...]}
    Returns:
        {"s3_key": "outputs/123/opinion_paper.pdf"}
    """
    try:
        analysis = event["analysis"]
        round_table_id = str(event["round_table_id"])
        district_codes = event.get("district_codes", [])

        # If no district codes provided, derive from analysis relevance
        if not district_codes and "district_relevance" in analysis:
            district_codes = [
                code
                for code, score in analysis["district_relevance"].items()
                if score >= 0.3
            ]

        logger.info(
            "Generating opinion paper for round table %s, districts=%s",
            round_table_id,
            district_codes,
        )

        html_content = OPINION_PAPER_TEMPLATE.render(
            title=analysis.get("title", "Round Table Discussion"),
            executive_summary=analysis.get("executive_summary", ""),
            core_theses=analysis.get("core_theses", []),
            key_disagreements=analysis.get("key_disagreements", []),
            consensus_points=analysis.get("consensus_points", []),
            key_quotes=analysis.get("key_quotes", []),
            recommendations=analysis.get("recommendations", []),
            participants_mentioned=analysis.get("participants_mentioned", []),
            round_table_id=round_table_id,
            district_codes=district_codes,
            district_names=DISTRICT_NAMES,
        )

        # Convert to PDF
        pdf_bytes = HTML(string=html_content).write_pdf()

        s3_key = f"outputs/{round_table_id}/opinion_paper.pdf"
        s3.put_object(
            Bucket=S3_BUCKET_OUTPUTS,
            Key=s3_key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        )
        logger.info(
            "Opinion paper uploaded to s3://%s/%s (%d bytes)",
            S3_BUCKET_OUTPUTS,
            s3_key,
            len(pdf_bytes),
        )

        return {"s3_key": s3_key}

    except Exception:
        logger.exception("Failed to generate opinion paper")
        raise
