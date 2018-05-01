#!/usr/bin/env python3
from slackclient import SlackClient
import time

# instantiate Slack client
slack_client = SlackClient("xoxb-354564967223-WrNuwJcaLWIYiBMh71EKnxPK")
starterbot_id = None

if slack_client.rtm_connect(with_team_state=False):
    print("Bot connected successfully!")
    starterbot_id = slack_client.api_call("auth.test")["user_id"]

    i = 0
    while True:
        slack_client.api_call(
            "chat.postMessage",
            channel="db_backups",
            text="test_{}".format(i)
        )
        i += 1
        time.sleep(1)

