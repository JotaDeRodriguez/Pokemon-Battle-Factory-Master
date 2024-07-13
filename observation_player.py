import asyncio
import json
import os

from poke_env.player import Player, RandomPlayer, cross_evaluate
from poke_env.environment.pokemon import Pokemon

from supervisor import supervisor
from utils import build_battle_prompt

def clear_memory():
    file_path = "battle_context/battle_context.json"
    try:
        # Open the file in write mode, which will clear its contents
        with open(file_path, "w") as battle_context:
            # Write an empty list to the file
            json.dump({"battle_messages": []}, battle_context)
        print("Debug: Battle context cleared. File has been reset.")
    except Exception as e:
        print(f"Error clearing memory: {e}")


class RealTimePlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _handle_battle_message(self, split_messages):
        # Call the base class method for default handling
        await super()._handle_battle_message(split_messages)

        # Handle each message in real-time
        for message in split_messages:
            self.handle_message(' '.join(message))

    def handle_message(self, raw_message):
        if not raw_message.strip():
            return "Empty message received."

        output_messages = []
        debug_messages = []

        def write_as_context(battle_message_history):
            file_path = "battle_context/battle_context.json"

            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Read existing data
            existing_data = []
            if os.path.exists(file_path):
                with open(file_path, "r") as battle_context:
                    try:
                        existing_data = json.load(battle_context).get('battle_messages', [])
                    except json.JSONDecodeError:
                        print("Debug: Existing file was empty or invalid JSON")

            # Append new messages
            if isinstance(battle_message_history, list):
                updated_data = existing_data + battle_message_history
            elif isinstance(battle_message_history, str):
                updated_data = existing_data + [battle_message_history]
            else:
                return

            # Write updated data back to file
            try:
                with open(file_path, "w") as battle_context:
                    json.dump({'battle_messages': updated_data}, battle_context, indent=2)
            except Exception as e:
                print(f"Error writing context: {e}")


        def replace_player(text):
            return text.replace("p1a", "Player").replace("p2a", "Rival").replace("p1", "Player").replace("p2", "Rival")

        lines = raw_message.strip().split('\n')
        for line in lines:
            line = line.strip()  # Ensure no leading/trailing whitespace
            # print(line)
            if not line:  # Skip empty lines
                continue

            parts = line.split()
            if not parts:
                continue

            if parts[0] == "switch":
                player, pokemon = parts[1:3]
                player = replace_player(player.rstrip('a:'))
                output_messages.append(f"{player.capitalize()} sent out {pokemon}!")

            elif parts[0] == "move":
                if len(parts) == 6:
                    attacker = replace_player(parts[1].rstrip(':'))
                    pokemon = parts[2]
                    move = replace_player(parts[3])
                    output_messages.append(f"{attacker}'s {pokemon} used {move}!")
                else:
                    attacker = replace_player(parts[1].rstrip(':'))
                    pokemon = parts[2]
                    move = replace_player(" ".join(parts[3:5]))
                    output_messages.append(f"{attacker}'s {pokemon} used {move}!")

            elif parts[0] == "-damage" and "fnt" not in line:
                player = replace_player(parts[1].rstrip(':'))
                pokemon = parts[2]
                health = parts[3]
                reason = " ".join(parts[4:]) if len(parts) > 4 else "the attack"
                output_messages.append(f"{player}'s {pokemon} took damage from {reason}! It's now at {health} HP.")

            elif parts[0] == "-resisted":
                player = replace_player(parts[1].rstrip(':'))
                pokemon = parts[2]
                output_messages.append(f"{player}'s {pokemon} resisted the attack!")

            elif parts[0] == "-supereffective":
                player = replace_player(parts[1].rstrip(':'))
                pokemon = parts[2]
                output_messages.append(f"Super-effective hit on {player}'s {pokemon}")

            elif parts[0] == "-crit":
                player = replace_player(parts[1].rstrip(':'))
                pokemon = parts[2]
                output_messages.append(f"A critical hit on {player}'s {pokemon}!")

            elif parts[0] == "faint":
                pokemon = parts[2]
                output_messages.append(f"{pokemon} fainted!")

            elif parts[0] == "-status":
                pokemon = parts[2]
                status = parts[3]
                status_full = {
                    'psn': 'poison',
                    'tox': 'toxic poison',
                    'brn': 'burn',
                    'par': 'paralysis',
                    'slp': 'sleep',
                    'frz': 'freeze'
                }.get(status, status)
                output_messages.append(f"{pokemon} was afflicted by {status_full}!")

            elif parts[0] == "-boost":
                players = replace_player(parts[1].rstrip(':'))
                pokemon = parts[2]
                stat = parts[3]
                amount = parts[4]
                stat_full = {
                    'atk': 'Attack',
                    'def': 'Defense',
                    'spa': 'Special Attack',
                    'spd': 'Special Defense',
                    'spe': 'Speed',
                    'acc': 'Accuracy',
                    'eva': 'Evasion'
                }.get(stat, stat)
                output_messages.append(f"{players}'s {pokemon}'s {stat_full} rose by {amount}!")

            elif parts[0] == "-activate":
                pokemon = parts[2]
                effect = " ".join(parts[2:])
                output_messages.append(f"{pokemon} was {effect}!")

            elif parts[0] == "-immune":
                pokemon = replace_player(parts[1].rstrip(':'))
                output_messages.append(f"{pokemon} was immune to the attack!")

            elif parts[0] == "-heal":
                pokemon = parts[2]
                health = parts[3]
                reason = parts[6] if len(parts) > 5 else " ".join(parts[4:5])
                output_messages.append(f"{pokemon} recovered health from {reason}. It's now at {health} HP.")

            elif parts[0] == "-weather":
                if "Rain Dance" in line:
                    output_messages.append(f"The weather is Rain!")
                else:
                    weather = " ".join(parts[1:])
                    output_messages.append(f"The weather is {weather}.")

            elif parts[0] == "turn":
                turn_number = parts[1]
                output_messages.append(f"Turn {turn_number} begins.")

            elif parts[0] == "-miss":
                player = replace_player(parts[1].rstrip(':'))
                pokemon = parts[2]
                target = parts[-1]
                output_messages.append(f"{player}'s {pokemon}'s attack missed {target}!")

            elif parts[0] == "-ability":
                player = replace_player(parts[1].rstrip(':'))
                pokemon = parts[2]
                ability_message = " ".join(parts[3:])
                output_messages.append(f"{player}'s {pokemon} ability activated: {ability_message}")

            else:
                # Debug: Print any lines not caught by the above conditions
                debug_messages.append(f"DEBUG: Unhandled line: {line}")
                # Print and return all messages

        all_messages = "\n".join(output_messages)
        battle_messages = all_messages.replace("\n", "")
        write_as_context(output_messages)

        # print(battle_messages.strip())  # Print all messages at once after processing

        return battle_messages


    def handle_request(self, message):
        if message[1]:  # Ensure there is data to decode
            try:
                request_data = json.loads(message[2])
                pretty_json = json.dumps(request_data, indent=4)
                print(pretty_json)

                for pokemon in request_data['side']['pokemon']:
                    print(pokemon['details'].split(',')[0])

            except json.JSONDecodeError:
                print("Error decoding JSON data")
        else:
            print("Empty request data")

    def choose_move(self, battle):

        def battle_info():

            if battle.available_moves:
                for move in battle.available_moves:
                    moves_data.append(move.id)

            if battle.available_switches:
                for mon in battle.available_switches:
                    switches_data.append(mon.species)

        current_pokemon_and_moves = []
        moves_data = []
        switches_data = []
        own_ability = []

        current_pokemon_and_moves.append(battle.active_pokemon.species)

        current_pokemon_and_moves.append(battle.opponent_active_pokemon.species)

        own_ability.append(battle.active_pokemon.ability)

        battle_info()
        current_pokemon_and_moves.extend([moves_data, switches_data, own_ability])

        print(current_pokemon_and_moves)

        def get_context():
            with open("battle_context/battle_context.json", "r") as file:
                data = json.load(file)
                messages = data["battle_messages"]

                # Check if messages list is empty
                if not messages:
                    return None

                # Reverse iterate over the list to find the last three "Turn" starts
                turns = []
                for i in range(len(messages) - 1, -1, -1):
                    if messages[i].startswith("Turn"):
                        turns.append(i)
                        if len(turns) == 3:
                            break

                # Check if there are fewer than three turns
                if len(turns) < 3:
                    if turns:
                        last_turns = messages[turns[-1]:]
                    else:
                        return ["The battle just began. Strategize accordingly"]
                else:
                    last_turns = messages[turns[-1]:]

                return last_turns

        context = get_context()
        if context:
            battle_context = build_battle_prompt(*current_pokemon_and_moves)

            full_context = context + battle_context
            print(full_context)
            call_gpt = supervisor(full_context)
            print(call_gpt)
            # pass
        # Chooses a move with the highest base power when possible

        if battle.available_moves:
            best_move = max(battle.available_moves, key=lambda move: move.base_power)
            # print(f"Chose {best_move}!")
            return self.create_order(best_move)
        else:
            # print("No available moves, switching")
            return self.choose_random_move(battle)


# Main execution setup
if __name__ == "__main__":

    clear_memory()
    random_player = RandomPlayer(battle_format="gen3randombattle")
    real_time_player = RealTimePlayer(battle_format="gen3randombattle")
    players = [real_time_player, random_player]

    asyncio.get_event_loop().run_until_complete(cross_evaluate(players, n_challenges=1))
