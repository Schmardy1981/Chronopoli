"""
Chronopoli Symposia – AWS IVS Client

Wrapper around boto3 IVS (Interactive Video Service) for creating
and managing live-stream channels used during Round Table sessions.
"""

import logging

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_ivs_client():
    """Return a boto3 IVS client configured from Django settings."""
    region = getattr(settings, "AWS_IVS_REGION", getattr(settings, "AWS_DEFAULT_REGION", "us-east-1"))
    return boto3.client("ivs", region_name=region)


def create_channel(round_table):
    """
    Create an AWS IVS channel for the given RoundTable instance.
    Saves the channel ARN, stream key, and playback URL back to the model.

    Args:
        round_table: A RoundTable model instance.

    Returns:
        dict with keys: channel_arn, stream_key, playback_url
        or None on failure.
    """
    client = _get_ivs_client()

    try:
        response = client.create_channel(
            name=f"chronopoli-rt-{round_table.slug}",
            latencyMode="LOW",
            type="STANDARD",
            tags={
                "platform": "chronopoli",
                "round_table_id": str(round_table.pk),
                "slug": round_table.slug,
            },
        )

        channel = response["channel"]
        stream_key = response["streamKey"]

        round_table.ivs_channel_arn = channel["arn"]
        round_table.ivs_stream_key = stream_key["value"]
        round_table.ivs_playback_url = channel["playbackUrl"]
        round_table.save(update_fields=[
            "ivs_channel_arn",
            "ivs_stream_key",
            "ivs_playback_url",
        ])

        logger.info(
            "IVS channel created for Round Table %s: %s",
            round_table.slug,
            channel["arn"],
        )

        return {
            "channel_arn": channel["arn"],
            "stream_key": stream_key["value"],
            "playback_url": channel["playbackUrl"],
        }

    except ClientError as exc:
        logger.error("Failed to create IVS channel for %s: %s", round_table.slug, exc)
        return None


def delete_channel(channel_arn):
    """
    Delete an AWS IVS channel by ARN.

    Args:
        channel_arn: The ARN of the IVS channel to delete.

    Returns:
        True on success, False on failure.
    """
    client = _get_ivs_client()

    try:
        client.delete_channel(arn=channel_arn)
        logger.info("IVS channel deleted: %s", channel_arn)
        return True
    except ClientError as exc:
        logger.error("Failed to delete IVS channel %s: %s", channel_arn, exc)
        return False


def get_stream_info(channel_arn):
    """
    Get current stream information for an IVS channel.

    Args:
        channel_arn: The ARN of the IVS channel.

    Returns:
        dict with stream info (state, health, viewerCount) or None if
        no active stream or on error.
    """
    client = _get_ivs_client()

    try:
        response = client.get_stream(channelArn=channel_arn)
        stream = response["stream"]
        return {
            "state": stream.get("state"),
            "health": stream.get("health"),
            "viewer_count": stream.get("viewerCount", 0),
            "start_time": stream.get("startTime"),
        }
    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        if error_code == "ChannelNotBroadcasting":
            logger.debug("No active stream for channel %s", channel_arn)
            return None
        logger.error("Failed to get stream info for %s: %s", channel_arn, exc)
        return None
