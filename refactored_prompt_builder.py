import json

from utils import load_type_data
from utils import get_moves_info, get_ability_description, get_ability_name


"""

Necessary information:

Current team info

"""


def remove(string):
    return string.replace(" ", "")


def build_battle_prompt(current_pokemon, opposing_pokemon):

    prompt_start = f"You're facing {opposing_pokemon}. Your current pokemon is {current_pokemon}."


    with open('battle_context/team_info.json', 'r') as file:
        data = json.load(file)

    moves_prompt = ['The moves of your Pokemon are:']

    for item in data['active']:
        for move in item['moves']:
            move_name = move['move']
            move_id = move['id']
            if "Hidden Power" in move_name:
                parts = move_name.split()
                move_name = " ".join(parts[0:3])
                move_id = remove(move_name)
            pp = move['pp']
            disabled = move['disabled']

            move_info = get_moves_info(move_id)
            move_type = move_info[move_id]['Type']
            move_effect = move_info[move_id]['Effect']
            move_power = move_info[move_id]['Power']

            if not disabled:
                if pp > 5:
                    prompt = f'{move_name}: A {move_type}-type move. Power {move_power}. {move_effect}'
                    moves_prompt.append(prompt)
                if pp < 5:
                    prompt = f'{move_name}: A {move_type}-type move. Move effect: {move_effect}. It only has {pp} power points left'
                    moves_prompt.append(prompt)
                if pp == 0:
                    prompt = f'{move_name} has no Power Points left.'
                    moves_prompt.insert(-1, prompt)
            else:
                prompt = f'The move {move_name} is currently disabled.'
                moves_prompt.insert(-1, prompt)


    full_moves_prompt = ('\n'.join(moves_prompt))

    switches_prompt = ["In your bench sit: "]
    ability_prompt = ["Its ability is: "]

    pokemon_list = data['side']['pokemon']
    print(pokemon_list)
    print()
    for pokemon in (p for p in pokemon_list if not p["active"]):
        details = pokemon['ident']
        parts = details.split()
        species = parts[1]
        species_id = species.lower()
        ability = pokemon["baseAbility"]


        condition = pokemon['condition']
        if condition != "0 fnt":
            hp = eval(condition) * 100
            hp_percentage = f"{hp:.2f}%"
            prompt = f"{species} with {hp_percentage} HP remaining."
            switches_prompt.append(prompt)

            moves = pokemon["moves"]
            ability_name = get_ability_name(ability)
            player_ability_description = get_ability_description(ability)

            prompt = f"It's ability is {ability_name}: {player_ability_description}"
            switches_prompt.append(prompt)

        if condition == "0 fnt":
            prompt = f"{species} is fainted, and unable to battle"
            switches_prompt.append(prompt)

    full_switches_prompt = "\n".join(switches_prompt)
    full_ability_prompt = ('\n'.join(ability_prompt))

    full_prompt = prompt_start + '\n' + full_moves_prompt + '\n' + full_switches_prompt + '\n'

    return full_prompt


prompt = build_battle_prompt("Swampert", "Blaziken")

print(prompt)
