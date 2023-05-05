import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request
from agents.snapshot_bot import SnapshotBot

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Set Slack API credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]

# Initialize the Slack app
app = App(token=SLACK_BOT_TOKEN)

# Initialize the Flask app
# Flask is a web application framework written in Python
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


def get_bot_user_id():
    """
    Get the bot user ID using the Slack API.
    Returns:
        str: The bot user ID.
    """
    try:
        # Initialize the Slack client with your bot token
        slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error: {e}")


def my_function(text):
    """
    Custom function to process the text and return a response.
    In this example, the function converts the input text to uppercase.

    Args:
        text (str): The input text to process.

    Returns:
        str: The processed text.
    """
    response = text.upper()
    return response


@app.event("app_mention")
def handle_mentions(body, say):
    
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.

    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """
    text = body["event"]["text"]

    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()

    # Extract niche, city, and state from the user input
    try:
        niche, city, state = [x.strip() for x in text.split(",")]
    except ValueError:
        say("Please provide the input in the format 'niche, city, state'")
        return
    
    say(f"Running analysis for {niche} in {city}, {state}...")
    
    # Use SnapshotBot to get the google front page results
    say("Getting search results...")
    location = f"{city}, {state}"
    search_results = SnapshotBot.get_search_results(niche, location)
    
    # Use SnapshotBot to process the map pack and organic results
    say("Cleaning search results to remove unnecessary data...")
    processed_map_pack = SnapshotBot.process_map_pack(search_results.get('map_pack'))
    processed_organic_results = SnapshotBot.process_organic_results(search_results.get('organic_results'))
    
    # Use SnapshotBot to count instances of prameters: city name in title, more than 10 reviews, and connected websites
    say("Analyzing data...")
    map_pack_analysis = SnapshotBot.analyze_map_pack(processed_map_pack, city)
    
    # Use SnapshotBot to count instances of parameters: city name in title, city name in link
    organic_analysis = SnapshotBot.analyze_organic_results(processed_organic_results, city)
    
    # Use SnapshotBot to compare niche to types of map pack results and descriptions of organic results
    type_and_description_analysis = SnapshotBot.analyze_types_and_descriptions(processed_map_pack, processed_organic_results, niche)
    # say(str(type_and_description_analysis))
    
    say("Preparing your competition scores...")
    # Use SnapshotBot to prepare the response in table format
    table_response = SnapshotBot.prepare_response(map_pack_analysis, organic_analysis, type_and_description_analysis)

    say(blocks=table_response)



@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """
    return handler.handle(request)


# Run the Flask app
if __name__ == "__main__":
    flask_app.run(port=8080)
