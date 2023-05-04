import os
from dotenv import find_dotenv, load_dotenv
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from flask_app.models.snapshot_bot import SnapshotBot
from flask_app import flask_app
from flask import request

load_dotenv(find_dotenv())
SLACK_BOT_TOKEN = os.environ["SNAPSHOT_BOT_TOKEN"]

slack_app = App(token=SLACK_BOT_TOKEN)
handler = SlackRequestHandler(slack_app)

@slack_app.event("app_mention")
def handle_mentions(body, say):
    say("Sure, I'll get right on that!")
    niche, city, state = SnapshotBot.process_message(body)

    # Get search results based on the extracted parameters
    location = f"{city}, {state}"
    search_results = SnapshotBot.get_search_results(niche, location)
    response = SnapshotBot.get_response_from_query(search_results, city)

    say(response)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)