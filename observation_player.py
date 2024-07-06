import asyncio
import json
import orjson

from poke_env.player import RandomPlayer, cross_evaluate

class StoragePlayer(RandomPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.battle_log = []  # Initialize a list to store messages

    async def _handle_battle_message(self, split_messages):
        # Increment turn and log messages
        global turn
        turn += 1
        self.battle_log.append(split_messages)

        # Call the base class method for default handling
        return await super()._handle_battle_message(split_messages)

def save_battle_log_to_file(battle_log):
    """ Saves battle log to a binary JSON file using orjson. """
    with open("msgs.json", "wb+") as f:
        f.write(orjson.dumps(battle_log))

def json_writer(file, content):
    """ Writes pretty formatted JSON to a file. """
    with open(file, "w") as json_file:
        json_file.write(content)

def parse_battle_log(battle_log):
    """ Parses and prints human-readable messages from the battle log. """
    for turn, messages in enumerate(battle_log):
        for message in messages:
            handle_message(message)
        print("\n")  # Newline for readability between turns

def handle_message(message):
    """ Handles individual messages based on their type. """
    if not message:
        return

    message_type = message[0]
    handlers = {
        'init': lambda msg: print(f"Battle started: {msg[2]}"),
        'title': lambda msg: print(f"Match: {msg[2]}"),
        'j': lambda msg: print(f"Player joined: {msg[2]}"),
        'gametype': lambda msg: print(f"Game type: {msg[1]}"),
        'player': lambda msg: print(f"Player {msg[2]}: {msg[3]}"),
        'request': handle_request,
        'move': lambda msg: print(f"Action: {' '.join(msg[1:])}"),
        'switch': lambda msg: print(f"Action: {' '.join(msg[1:])}"),
        'turn': lambda msg: print(f"Turn {msg[1]}")
    }
    if message_type in handlers:
        handlers[message_type](message)
    else:
        print(f"Message: {' '.join(message)}")

def handle_request(message):
    """ Processes and prints details from request messages. """
    if message[1]:  # Ensure there is data to decode
        try:
            request_data = json.loads(message[2])
            pretty_json = json.dumps(request_data, indent=4)
            print(pretty_json)
            json_writer("output.json", pretty_json)

            for pokemon in request_data['side']['pokemon']:
                print(pokemon['details'].split(',')[0])

        except json.JSONDecodeError:
            print("Error decoding JSON data")
    else:
        print("Empty request data")

# Main execution setup
if __name__ == "__main__":
    turn = 0  # Global turn counter

    random_player = RandomPlayer(battle_format="gen3randombattle")
    log_player = StoragePlayer(battle_format="gen3randombattle")
    players = [log_player, random_player]

    asyncio.get_event_loop().run_until_complete(cross_evaluate(players, n_challenges=1))
    save_battle_log_to_file(log_player.battle_log)
    parse_battle_log(log_player.battle_log)