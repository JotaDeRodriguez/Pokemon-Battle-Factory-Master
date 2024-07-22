import json
from typing import List, Dict
from collections import defaultdict

def load_type_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def load_team_data(file_path: str) -> Dict:
    """Load team data from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def get_pokemon_type(pokemon_name):
    pokemon_type = load_type_data("information/Gen III - Pokemon List.json")
    type_info = {}
    for pokemon in pokemon_type:
        if pokemon["Pokemon Name"].lower() == pokemon_name.lower():
            types = [pokemon["Type"]]
            if pokemon.get("Type2"):
                types.append(pokemon["Type2"])
            type_info[pokemon_name] = types
            break
    return type_info

def get_pokemon_ability(pokemon_name):
    ability_info = load_type_data("information/Gen III - Abilities.json")
    ability_list = []

    for ability in ability_info:
        description = ability_info[ability]['Description']
        learnt_by = ability_info[ability]['Learnt By']
        ability_name = ability_info[ability]['Name']

        if pokemon_name.capitalize() in learnt_by:
            full_description = f"{ability_name}: {description}"
            ability_list.append(full_description)

    if len(ability_list) > 1:
        return "The pokemon can have one of two possible abilities: " + " ".join(ability_list)
    else:
        return ability_list[0] if ability_list else "No ability information found."

def get_ability_description(ability_id):
    ability_info = load_type_data("information/Gen III - Abilities.json")
    description = ability_info[ability_id]['Description']
    return description

def get_ability_name(ability_id):
    ability_name = load_type_data("information/Gen III - Abilities.json")
    name = ability_name[ability_id]['Name']
    return name

def get_moves_info(move):
    moves_data = load_type_data("information/Gen III - Move List.json")
    move_lower = move.lower()
    moves_data_lower = {key.lower(): value for key, value in moves_data.items()}

    if move_lower in moves_data_lower:
        move_info = moves_data_lower[move_lower]
        move_info = {
            "Effect": move_info.get("Effect", "No effect info available"),
            "Type": move_info.get("Type", "No type info available"),
            "Power": move_info.get("Power", "No power info available"),
            "Accuracy": move_info.get("Accuracy", "No accuracy info available"),
            "id": move_info.get("id", "No id found"),
            "Name": move_info.get("Name", "No name info available")
        }
    else:
        move_info = {"Error": "Move not found"}

    return {move: move_info}

def get_defending_type_interaction(defending_type):
    type_advantages = load_type_data("information/Gen III - Defending Type Chart.json")

    interactions = {
        'super effective': [],
        'not very effective': [],
        'no effect': [],
        'normal damage': []
    }
    for attacking_type, multiplier in type_advantages[defending_type].items():
        if multiplier > 1:
            interactions['super effective'].append(attacking_type)
        elif multiplier == 0.5:
            interactions['not very effective'].append(attacking_type)
        elif multiplier == 1:
            interactions['normal damage'].append(attacking_type)
        elif multiplier == 0:
            interactions['no effect'].append(attacking_type)

    return interactions

def get_combined_type_interaction(typing):
    if len(typing) == 1:
        return get_defending_type_interaction(typing[0])

    double_type_interactions = [get_defending_type_interaction(type) for type in typing]

    combined_interactions = {
        'four times effective': [],
        'super effective': [],
        'not very effective': [],
        'almost ineffective': [],
        'no effect': [],
        'normal damage': []
    }

    interaction_counts = defaultdict(lambda: defaultdict(int))

    for interaction_dict in double_type_interactions:
        for key, values in interaction_dict.items():
            for value in values:
                interaction_counts[value][key] += 1

    for value, categories in interaction_counts.items():
        if categories['no effect'] > 0:
            combined_interactions['no effect'].append(value)
        else:
            effective_count = categories['super effective']
            not_effective_count = categories['not very effective']

            if effective_count > 0 and not_effective_count > 0:
                combined_interactions['normal damage'].append(value)
            else:
                if effective_count > 1:
                    combined_interactions['four times effective'].append(value)
                elif effective_count == 1:
                    combined_interactions['super effective'].append(value)
                if not_effective_count > 1:
                    combined_interactions['almost ineffective'].append(value)
                elif not_effective_count == 1:
                    combined_interactions['not very effective'].append(value)

    for value in interaction_counts:
        if value not in combined_interactions['no effect'] and value not in combined_interactions['normal damage']:
            if interaction_counts[value]['super effective'] == 0 and interaction_counts[value]['not very effective'] == 0:
                combined_interactions['normal damage'].append(value)

    return combined_interactions

def format_move_info(move: Dict, opposing_pokemon_type: List[str]) -> str:
    """Format information about a single move, including effectiveness against the opposing Pokémon."""
    move_name = move['move']
    move_id = move['id']
    pp = move['pp']
    disabled = move['disabled']

    if "Hidden Power" in move_name:
        move_name = " ".join(move_name.split()[:3])
        move_id = move_name.replace(" ", "").lower()

    move_info = get_moves_info(move_id)
    move_type = move_info[move_id]['Type']
    move_effect = move_info[move_id]['Effect']
    move_power = move_info[move_id]['Power']

    if disabled:
        return f"The move {move_name} is currently disabled."

    if pp == 0:
        return f"{move_name} has no Power Points left."

    type_interactions = get_combined_type_interaction(opposing_pokemon_type)
    effectiveness = ""

    # Use .get() method with a default value of an empty list
    if move_type in type_interactions.get('four times effective', []):
        effectiveness += "This move will do four times the damage. "
    if move_type in type_interactions.get('super effective', []):
        effectiveness += "This move is super effective! "
    if move_type in type_interactions.get('not very effective', []):
        effectiveness += "This move is not very effective. "
    if move_type in type_interactions.get('almost ineffective', []):
        effectiveness += "This move will only do one quarter damage. "
    if move_type in type_interactions.get('no effect', []):
        effectiveness += "But this move will have no effect. "

    base_info = f"{move_name}: A {move_type}-type move. Power {move_power}. {move_effect}{effectiveness}"

    if pp < 5:
        return f"{base_info} It only has {pp} power points left."

    return base_info

def format_pokemon_info(pokemon: Dict, opposing_pokemon_type: List[str]) -> str:
    """Format information about a single Pokémon, including super-effective moves."""
    species = pokemon['ident'].split(': ')[1]
    condition = pokemon['condition']

    if condition == "0 fnt":
        return f"{species} is fainted, and unable to battle."

    hp_percentage = f"{(eval(condition) * 100):.2f}%"
    ability_name = get_ability_name(pokemon["baseAbility"])
    ability_description = get_ability_description(pokemon["baseAbility"])

    super_effective_moves = []
    type_interactions = get_combined_type_interaction(opposing_pokemon_type)

    for move_id in pokemon['moves']:
        print(move_id)
        move_info = get_moves_info(move_id)
        if isinstance(move_info, dict) and move_id in move_info:
            move_type = move_info[move_id]['Type']
            move_name = move_info[move_id]['Name']
            if (move_type in type_interactions.get('four times effective', []) or
                move_type in type_interactions.get('super effective', [])):
                super_effective_moves.append(move_name)
        else:
            print(f"Warning: Unable to get move info for {move_id}")

    base_info = f"{species} with {hp_percentage} HP remaining.\n" \
                f"Its ability is {ability_name}: {ability_description}"

    if super_effective_moves:
        base_info += f"\nIt has super-effective moves against the current pokemon: {', '.join(super_effective_moves)}"

    return base_info

def build_battle_prompt(current_pokemon: str, opposing_pokemon: str, current_ability: str):
    """Build a comprehensive battle prompt based on the current team situation."""
    team_data = load_team_data('battle_context/team_info.json')

    current_pokemon_ability = get_ability_description(current_ability)
    opposing_pokemon_ability = get_pokemon_ability(opposing_pokemon)
    opposing_pokemon_type_dict = get_pokemon_type(opposing_pokemon)
    opposing_pokemon_type = opposing_pokemon_type_dict[opposing_pokemon]
    prompt_parts = [
        f"You're facing {opposing_pokemon}. Your current pokemon is {current_pokemon}.",
        f"\nYour {current_pokemon}'s ability: {current_ability}{current_pokemon_ability}",
        f"\nOpposing {opposing_pokemon}'s ability: {opposing_pokemon_ability}",
        "\nYour active Pokémon's moves are:"
    ]

    # Format active Pokémon's moves
    for pokemon in team_data['active']:
        prompt_parts.extend(format_move_info(move, opposing_pokemon_type) for move in pokemon['moves'])

    prompt_parts.append("\nIn your bench sit:")

    # Format bench Pokémon information
    for pokemon in (p for p in team_data['side']['pokemon'] if not p["active"]):
        prompt_parts.append(format_pokemon_info(pokemon, opposing_pokemon_type))

    return '\n'.join(prompt_parts)