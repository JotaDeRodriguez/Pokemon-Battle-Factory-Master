import json
from claudes_refactored_prompt_builder import build_battle_prompt


def get_context():
    with open("battle_context/battle_context.json", "r") as file:
        data = json.load(file)
        messages = data["battle_messages"]

        # Check if messages list is empty
        if not messages:
            return ["The battle is starting. Make a strategy!"]

        # Reverse iterate over the list to find the last three "Turn" starts
        turns = []
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].startswith("Turn"):
                turns.append(i)
                if len(turns) == 3:
                    break

        # Check if there are fewer than three turns
        if len(turns) < 1:
            if turns:
                last_turns = messages[turns[-1]:]
            else:
                return ["The battle just began. Strategize accordingly"]
        else:
            last_turns = messages[turns[-1]:]

        return last_turns


current_pokemon = ["Rapidash", "Regice", "blaze"]
context_list = get_context()

context = "\n".join(context_list)
battle_context = build_battle_prompt(str(current_pokemon[0]), str(current_pokemon[1]), str("".join(current_pokemon[2])))
full_context = "Summary of the last three turns: " "\n" + "\n" + context + "\n" + "\n" + "Prompt Context: " + battle_context
print(full_context)

full_context = "Summary of the last three turns: " + context + "\n" + "Prompt Context: " + battle_context
