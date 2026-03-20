"""
Chronopoli AI Tutor — Amazon Bedrock Client

Retrieves context from Knowledge Base, generates streaming responses via Claude.
"""

import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

_bedrock_agent = None
_bedrock_runtime = None


def _get_clients():
    global _bedrock_agent, _bedrock_runtime
    if _bedrock_agent is None:
        import boto3

        region = getattr(settings, "AWS_REGION", "me-central-1")
        _bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=region)
        _bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
    return _bedrock_agent, _bedrock_runtime


def retrieve_context(question: str, num_results: int = 8) -> list:
    """
    Retrieve relevant context from the Bedrock Knowledge Base.

    Returns list of {"content": str, "uri": str, "score": float}
    """
    agent_client, _ = _get_clients()
    kb_id = getattr(settings, "BEDROCK_KNOWLEDGE_BASE_ID", "")

    if not kb_id:
        logger.warning("BEDROCK_KNOWLEDGE_BASE_ID not configured")
        return []

    try:
        response = agent_client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={"text": question},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": num_results}
            },
        )

        results = []
        for item in response.get("retrievalResults", []):
            content = item.get("content", {}).get("text", "")
            uri = item.get("location", {}).get("s3Location", {}).get("uri", "")
            score = item.get("score", 0.0)
            results.append({"content": content, "uri": uri, "score": score})

        return results
    except Exception as e:
        logger.error("Bedrock KB retrieval failed: %s", e)
        return []


def generate_streaming_response(
    messages: list,
    system_prompt: str,
    context_chunks: list,
) -> "Generator[str, None, None]":
    """
    Generate a streaming response from Bedrock Claude.

    Args:
        messages: list of {"role": "user"|"assistant", "content": str}
        system_prompt: personalized system prompt
        context_chunks: retrieved KB context

    Yields: text chunks as they stream in
    """
    _, runtime_client = _get_clients()
    model_id = getattr(
        settings, "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
    )

    # Build context block from KB retrieval
    if context_chunks:
        context_text = "\n\n---\n\n".join(
            f"[Source: {c['uri']}]\n{c['content']}" for c in context_chunks
        )
        augmented_system = (
            f"{system_prompt}\n\n"
            f"## Retrieved Knowledge Base Context:\n\n{context_text}\n\n"
            f"Use the above context to inform your answer. "
            f"Cite sources using [Source: ...] notation."
        )
    else:
        augmented_system = system_prompt

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "system": augmented_system,
        "messages": messages,
    }

    try:
        response = runtime_client.invoke_model_with_response_stream(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
        )

        for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                text = chunk.get("delta", {}).get("text", "")
                if text:
                    yield text
    except Exception as e:
        logger.error("Bedrock streaming failed: %s", e)
        yield f"\n\n[Error: AI Tutor temporarily unavailable. Please try again.]"


def sync_knowledge_base():
    """
    Trigger a Bedrock Knowledge Base sync (data source ingestion).
    Called after new content is approved (Symposia outputs, courses, etc.)
    """
    agent_client, _ = _get_clients()
    kb_id = getattr(settings, "BEDROCK_KNOWLEDGE_BASE_ID", "")
    ds_id = getattr(settings, "BEDROCK_DATA_SOURCE_ID", "")

    if not kb_id or not ds_id:
        logger.warning("Bedrock KB/DS IDs not configured — skipping sync")
        return

    try:
        agent_client.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id,
        )
        logger.info("Bedrock KB ingestion job started for %s", kb_id)
    except Exception as e:
        logger.error("Bedrock KB sync failed: %s", e)
