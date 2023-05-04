# main.py
from snapshot_bot import SnapshotBot
from due_diligence_bot import DueDiligenceBot

def handle_request(request):
    # Determine which bot needs to be initialized based on the request
    if request["bot_type"] == "snapshot_bot":
        bot = SnapshotBot(request["parameters"])
    elif request["bot_type"] == "due_diligence_bot":
        bot = DueDiligenceBot(request["parameters"])
    else:
        raise ValueError("Invalid bot type")

    # Process the request using the initialized bot
    response = bot.process_request(request)
    return response

# Example usage
request = {
    "bot_type": "snapshot_bot",
    "parameters": {...},
    ...
}

response = handle_request(request)
