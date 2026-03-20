"""
Chronopoli Master Class — Celery Tasks

Async processing for document extraction, question generation,
voice cloning, and avatar video creation.
"""

import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# Celery task decorators — graceful fallback if Celery not available
try:
    from celery import shared_task
except ImportError:
    def shared_task(func):
        func.delay = lambda *a, **kw: func(*a, **kw)
        return func


@shared_task
def process_document(document_id):
    """
    Process an uploaded expert document:
    1. Extract text via AWS Textract
    2. Analyze with Claude (core theses, expertise boundaries, key insights)
    3. Update TwinDocument and DigitalTwin models
    """
    from .models import TwinDocument

    doc = TwinDocument.objects.get(pk=document_id)
    twin = doc.twin

    try:
        import boto3

        region = getattr(settings, "AWS_REGION", "me-central-1")

        # Step 1: Textract
        textract = boto3.client("textract", region_name=region)
        bucket = getattr(settings, "S3_MEDIA_BUCKET", "")

        response = textract.detect_document_text(
            Document={"S3Object": {"Bucket": bucket, "Name": doc.s3_key}}
        )

        extracted_text = "\n".join(
            block["Text"]
            for block in response.get("Blocks", [])
            if block["BlockType"] == "LINE"
        )
        doc.extracted_text = extracted_text

        # Step 2: Claude analysis via Bedrock
        bedrock = boto3.client("bedrock-runtime", region_name=region)
        model_id = getattr(
            settings, "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )

        analysis_prompt = f"""Analyze this expert document and extract:
1. core_theses: 3-7 main positions or arguments
2. expertise_boundaries: what the expert IS and IS NOT an authority on
3. key_insights: 5-10 unique insights not commonly known
4. controversial_claims: any claims that might be challenged
5. knowledge_gaps: areas the document doesn't cover

Document text:
{extracted_text[:15000]}

Return ONLY valid JSON."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": analysis_prompt}],
        })

        result = bedrock.invoke_model(
            modelId=model_id, body=body, contentType="application/json"
        )
        result_body = json.loads(result["body"].read())
        analysis = json.loads(result_body["content"][0]["text"])

        doc.analysis = analysis
        doc.save(update_fields=["extracted_text", "analysis"])

        # Update twin expertise summary
        twin.expertise_summary = analysis.get("core_theses", [""])[0] if analysis.get("core_theses") else ""
        twin.status = "review"
        twin.save(update_fields=["expertise_summary", "status"])

        logger.info("Document %s processed for twin %s", document_id, twin.name)

    except Exception as e:
        logger.error("Document processing failed for %s: %s", document_id, e)


@shared_task
def generate_questions(twin_id):
    """
    Generate interview questions based on all processed documents for a twin.
    """
    from .models import DigitalTwin, GeneratedQuestion, TwinDocument

    twin = DigitalTwin.objects.get(pk=twin_id)
    documents = TwinDocument.objects.filter(twin=twin).exclude(analysis={})

    if not documents.exists():
        logger.warning("No processed documents for twin %s", twin_id)
        return

    # Combine all document analyses
    combined_knowledge = "\n\n".join(
        json.dumps(doc.analysis, indent=2) for doc in documents
    )

    try:
        import boto3

        region = getattr(settings, "AWS_REGION", "me-central-1")
        bedrock = boto3.client("bedrock-runtime", region_name=region)
        model_id = getattr(
            settings, "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )

        prompt = f"""Based on this expert's knowledge analysis, generate 20 interview questions
across 4 categories (5 per category):

1. foundation: Establish the expert's core expertise and credentials
2. deep_dive: Explore specific insights and unique perspectives
3. confrontational: Challenge assumptions and probe weaknesses
4. audience: Questions the audience would likely ask

Expert knowledge:
{combined_knowledge[:10000]}

Return a JSON array of objects with: category, question, suggested_answer
Return ONLY valid JSON."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}],
        })

        result = bedrock.invoke_model(
            modelId=model_id, body=body, contentType="application/json"
        )
        result_body = json.loads(result["body"].read())
        questions = json.loads(result_body["content"][0]["text"])

        # Clear existing questions and create new ones
        GeneratedQuestion.objects.filter(twin=twin).delete()
        for i, q in enumerate(questions):
            GeneratedQuestion.objects.create(
                twin=twin,
                question_text=q.get("question", ""),
                suggested_answer=q.get("suggested_answer", ""),
                category=q.get("category", "foundation"),
                order=i + 1,
            )

        logger.info("Generated %d questions for twin %s", len(questions), twin.name)

    except Exception as e:
        logger.error("Question generation failed for twin %s: %s", twin_id, e)


@shared_task
def clone_voice(twin_id, audio_s3_key):
    """Clone expert voice via ElevenLabs API."""
    from .models import DigitalTwin

    twin = DigitalTwin.objects.get(pk=twin_id)

    try:
        import boto3
        import requests

        api_key = getattr(settings, "ELEVENLABS_API_KEY", "")
        if not api_key:
            logger.warning("ELEVENLABS_API_KEY not configured")
            return

        # Download audio from S3
        region = getattr(settings, "AWS_REGION", "me-central-1")
        s3 = boto3.client("s3", region_name=region)
        bucket = getattr(settings, "S3_MEDIA_BUCKET", "")

        audio_obj = s3.get_object(Bucket=bucket, Key=audio_s3_key)
        audio_data = audio_obj["Body"].read()

        # Upload to ElevenLabs for voice cloning
        resp = requests.post(
            "https://api.elevenlabs.io/v1/voices/add",
            headers={"xi-api-key": api_key},
            data={"name": f"chronopoli-twin-{twin.pk}", "description": twin.name},
            files={"files": ("voice_sample.mp3", audio_data, "audio/mpeg")},
            timeout=120,
        )
        resp.raise_for_status()

        voice_id = resp.json().get("voice_id", "")
        twin.elevenlabs_voice_id = voice_id
        twin.save(update_fields=["elevenlabs_voice_id"])

        logger.info("Voice cloned for twin %s: %s", twin.name, voice_id)

    except Exception as e:
        logger.error("Voice cloning failed for twin %s: %s", twin_id, e)


@shared_task
def generate_avatar_video(twin_video_id):
    """Generate avatar video via HeyGen API."""
    from .models import TwinVideo

    video = TwinVideo.objects.select_related("twin").get(pk=twin_video_id)
    twin = video.twin

    try:
        import requests

        api_key = getattr(settings, "HEYGEN_API_KEY", "")
        if not api_key:
            logger.warning("HEYGEN_API_KEY not configured")
            return

        video.status = "generating"
        video.save(update_fields=["status"])

        # Create HeyGen video
        resp = requests.post(
            "https://api.heygen.com/v2/video/generate",
            headers={
                "X-Api-Key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "video_inputs": [{
                    "character": {
                        "type": "avatar",
                        "avatar_id": twin.heygen_avatar_id or "default",
                    },
                    "voice": {
                        "type": "text",
                        "input_text": video.script_text,
                        "voice_id": twin.elevenlabs_voice_id or "default",
                    },
                }],
                "dimension": {"width": 1920, "height": 1080},
            },
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()

        video.heygen_video_id = result.get("data", {}).get("video_id", "")
        video.status = "ready"
        video.save(update_fields=["heygen_video_id", "status"])

        logger.info("Avatar video generated for twin %s: %s", twin.name, video.heygen_video_id)

    except Exception as e:
        video.status = "failed"
        video.save(update_fields=["status"])
        logger.error("Avatar video generation failed: %s", e)
