#!/usr/bin/env python3
from slackclient import SlackClient
import time

def get_connected_slack_client(secrets_env):
    try:
        slack_client = SlackClient(secrets_env.str('SLACK_TOKEN'))
        if slack_client.rtm_connect(with_team_state=False):
            return slack_client
    except Exception:
        pass
    return None

def initialize_slack(secrets_env):
    global slack_client
    slack_client = get_connected_slack_client(secrets_env)

def safe_send_msg(msg: str):
    if slack_client is None:
        return
    slack_client.api_call(
        "chat.postMessage",
        channel="db_backups",
        text=msg
    )

def send_success_notification(dev_db_link: str, seconds_elapsed: int):
    msg = "Databases backed up successfully in {} seconds. *Dev DB download link:* {}".format(
        seconds_elapsed, dev_db_link,
    )
    safe_send_msg(msg)

def send_error_notification(error_msg: str):
    msg = "*Failed to back up databases:* ```{}```".format(error_msg)
    safe_send_msg(msg)
