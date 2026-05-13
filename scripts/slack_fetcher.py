"""
slack_fetcher.py
Fetches recent messages from specified Slack channels.
"""

import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def fetch_slack_messages(token: str, channels: list[str],
                         lookback_hours: int = 24,
                         max_per_channel: int = 10) -> list[dict]:
    """
    Returns a list of Slack message dicts for Claude to triage.
    Each dict has: channel, text, sender, received_iso, thread_url, needs_reply
    """
    client = WebClient(token=token)
    since_ts = (
        datetime.datetime.utcnow() - datetime.timedelta(hours=lookback_hours)
    ).timestamp()

    messages = []

    # Build a user ID → display name cache
    user_cache = {}

    def get_username(user_id: str) -> str:
        if user_id in user_cache:
            return user_cache[user_id]
        try:
            info = client.users_info(user=user_id)
            name = info["user"]["profile"].get("display_name") or info["user"]["name"]
            user_cache[user_id] = name
            return name
        except Exception:
            return user_id

    for channel_name in channels:
        clean = channel_name.lstrip("#")
        try:
            # Find channel ID by name
            cursor = None
            channel_id = None
            while True:
                resp = client.conversations_list(
                    types="public_channel,private_channel",
                    limit=200,
                    cursor=cursor,
                )
                for ch in resp["channels"]:
                    if ch["name"] == clean:
                        channel_id = ch["id"]
                        break
                if channel_id:
                    break
                cursor = resp.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break

            if not channel_id:
                print(f"  Channel #{clean} not found — check the name or bot access")
                continue

            # Fetch messages
            resp = client.conversations_history(
                channel=channel_id,
                oldest=str(since_ts),
                limit=max_per_channel,
            )

            for msg in resp.get("messages", []):
                if msg.get("subtype"):  # skip join/leave events
                    continue
                text = msg.get("text", "").strip()
                if not text:
                    continue

                user_id = msg.get("user", "")
                sender = get_username(user_id) if user_id else "unknown"
                ts = float(msg.get("ts", 0))
                received = datetime.datetime.utcfromtimestamp(ts).isoformat()

                # Build a Slack deep link
                channel_link = f"https://slack.com/app_redirect?channel={channel_id}"

                messages.append({
                    "channel": f"#{clean}",
                    "text": text[:1500],  # cap to save tokens
                    "sender": sender,
                    "received_iso": received,
                    "link": channel_link,
                    "source_label": f"Slack — #{clean}",
                })

        except SlackApiError as e:
            print(f"  Slack error for #{clean}: {e.response['error']}")
            continue

    return messages
