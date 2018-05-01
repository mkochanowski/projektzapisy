#!/usr/bin/env python3
from slackclient import SlackClient
import time

def get_connected_slack_client():
    try:
        slack_client = SlackClient("xoxb-354564967223-WrNuwJcaLWIYiBMh71EKnxPK")
        if slack_client.rtm_connect(with_team_state=False):
            return slack_client
    except Exception:
        pass
    return None

slack_client = get_connected_slack_client()

def safe_send_msg(msg):
    if slack_client is None:
        return
    slack_client.api_call(
        "chat.postMessage",
        channel="db_backups",
        text=msg
    )

def send_success_notification(dev_db_link):
    msg = "Databases backed up successfully. **Dev DB download link:** {}".format(dev_db_link)
    safe_send_msg(msg)

def send_error_notification(error_msg):
    msg = "**Failed to back up databases:** {}".format(error_msg)
    safe_send_msg(msg)
