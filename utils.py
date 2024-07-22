import json
from collections import defaultdict


# Load type advantage data from a JSON file
def load_type_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def get_pokemon_type(pokemon_name):

    pokemon_type = load_type_data("information/Gen III - Pokemon List.json")

    type_info = {}

    # Search through the list for the specified Pokémon
    for pokemon in pokemon_type:
        if pokemon["Pokemon Name"].lower() == pokemon_name.lower():  # Case insensitive comparison
            types = [pokemon["Type"]]
            if pokemon.get("Type2"):
                types.append(pokemon["Type2"])

            type_info[pokemon_name] = types
            break

    return type_info


def get_pokemon_ability(pokemon_name):

    # to do: Fix json, remove periods and commas.

    ability_info = load_type_data("information/Gen III - Abilities.json")

    ability_list = []

    for ability in ability_info:
        description = ability_info[ability]['Description']
        learnt_by = ability_info[ability]['Learnt By']
        ability_name = ability_info[ability]['Name']

        if pokemon_name.capitalize() in learnt_by:
            full_description = str(ability_name + ":" + " " + description)
            ability_list.append(full_description)

    if len(ability_list)>1:
        string = "The pokemon can have one of two possible abilities:"
        string_list = string + " " + " ".join(ability_list)
        return string_list
    else:
        return ability_list


def get_ability_description(ability_id):

    ability_info = load_type_data("information/Gen III - Abilities.json")
    description = ability_info[ability_id]['Description']

    return description

def get_ability_name(ability_id):
    ability_name = load_type_data("information/Gen III - Abilities.json")
    name = ability_name[ability_id]['Name']

    return name


def get_moves_info(move):
    # Load the moves data from the JSON file
    moves_data = load_type_data(
        r"information/Gen III - Move List.json")

    # Normalize the move input to lowercase
    move_lower = move.lower()

    # Create a case-insensitive mapping of moves_data
    moves_data_lower = {key.lower(): value for key, value in moves_data.items()}

    if move_lower in moves_data_lower:
        move_info = moves_data_lower[move_lower]
        # Construct the dictionary with move info
        move_info = {
            "Effect": move_info.get("Effect", "No effect info available"),
            "Type": move_info.get("Type", "No type info available"),
            "Power": move_info.get("Power", "No power info available"),
            "Accuracy": move_info.get("Accuracy", "No accuracy info available"),
            "id": move_info.get("id", "No id found"),
            "Name": move_info.get("Name", "No name info available")
        }
    else:
        move_info = "Move not found"

    # Return the move information, encapsulated under the original move name
    return {move: move_info}


def describe_move(move):
    move_info = get_moves_info(move)
    move_info = move_info[move]  # Access the move info dictionary

    if move_info == "Move not found":
        return f"The move '{move}' is not found in the database."

    # Extract move details
    effect = move_info['Effect']
    type_ = move_info['Type']
    power = move_info['Power']
    accuracy = move_info['Accuracy']

    # Construct the natural language description
    description = (f"'{move}' is a {type_} type move with a power of {power}, "
                   f"accuracy of {accuracy}, and the following effect: {effect}.")
    return description


def move_to_id(move):
    move_info = get_moves_info(move)
    move_info = move_info[move]  # Access the move info dictionary

    if move_info == "Move not found":
        return None

    # Extract move details
    id = move_info['id']

    return id


# Function to get type interactions in a simplified dictionary format
def get_attacking_type_interaction(attacking_type):
    type_advantages = load_type_data("information/Gen III - Attacking Type Chart.json")

    interactions = {
        'super effective': [],
        'not very effective': [],
        'no effect': [],
        'normal damage': []
    }
    for defending_type, multiplier in type_advantages[attacking_type].items():
        if multiplier > 1:
            interactions['super effective'].append(defending_type)
        elif multiplier == 0.5:
            interactions['not very effective'].append(defending_type)
        elif multiplier == 1:
            interactions['normal damage'].append(defending_type)
        elif multiplier == 0:
            interactions['no effect'].append(defending_type)
    return interactions


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
        type_interactions = get_defending_type_interaction(typing[0])
        return type_interactions

    if len(typing) > 1:
        double_type_interactions = []

        for type in typing:
            interactions = get_defending_type_interaction(type)
            double_type_interactions.append(interactions)

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

        # Processing the type interactions
        for value, categories in interaction_counts.items():
            if categories['no effect'] > 0:
                combined_interactions['no effect'].append(value)
                continue

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



def build_battle_prompt(player_pokemon, opponent_pokemon, player_moves, bench, own_ability):
    def get_type_effectiveness(pokemon):
        types = get_pokemon_type(pokemon)
        pokemon_type = types[pokemon]
        effectiveness = get_combined_type_interaction(pokemon_type)

        descriptions = {
            'four times effective': 'four times weak to',
            'super effective': 'weak to',
            'not very effective': 'resistant to',
            'almost ineffective': 'very resistant to',
            'no effect': 'immune to'
        }

        type_info = []
        for effect, desc in descriptions.items():
            if effect in effectiveness and effectiveness[effect]:
                capitalized_types = [attack_type.capitalize() for attack_type in effectiveness[effect]]
                type_info.append(f"{desc} {', '.join(capitalized_types)}")

        if 'normal damage' in effectiveness and effectiveness['normal damage']:
            capitalized_normal_types = [attack_type.capitalize() for attack_type in effectiveness['normal damage']]
            type_info.append(f"takes normal damage from {', '.join(capitalized_normal_types)}")

        return f"{pokemon.capitalize()} is {'. It '.join(type_info)}"


    if player_moves:
        player_type_info = get_type_effectiveness(player_pokemon)
        player_ability = ' '.join(own_ability)
        player_ability_description = get_ability_description(player_ability)

        opponent_type_info = get_type_effectiveness(opponent_pokemon)
        opponent_ability = get_pokemon_ability(opponent_pokemon)

        bench_info = ', '.join(pokemon.capitalize() for pokemon in bench)

        moves_info = ', '.join(move.capitalize() for move in player_moves)

        prompt = f"""
            Battle situation:
            - You are using {player_pokemon.capitalize()} with the ability {player_ability.capitalize()}: {player_ability_description}
                - Your moves: {moves_info}
                - Remember that {player_type_info}
    
            - Your opponent is using a {opponent_pokemon.capitalize()} (ability: {"".join(opponent_ability)}).
            - {opponent_type_info}
    
            - The pokemon on your bench are: {bench_info}
            """

        return prompt.strip()
    else:
        player_type_info = get_type_effectiveness(player_pokemon)
        player_ability = ' '.join(own_ability)
        player_ability_description = get_ability_description(player_ability)

        opponent_type_info = get_type_effectiveness(opponent_pokemon)
        opponent_ability = get_pokemon_ability(opponent_pokemon)

        bench_info = ', '.join(pokemon.capitalize() for pokemon in bench)

        prompt = f"""
                    On the last turn, your {player_pokemon.capitalize()} was fainted by the rival's {opponent_pokemon.capitalize()}.
                    {opponent_type_info}
                    Ability:
                    {"".join(opponent_ability)}

                    At this moment you can only choose between {bench_info} to send out to the field. 
                    Choose a Pokemon considering type advantages and your strategy.
                    
                    """

        return prompt.strip()


# # Usage
# info = ['lapras', 'hitmonchan', [],
#         ['jynx', 'magneton', 'gligar', 'manectric', 'volbeat'], ['truant']]
#
# prompt = build_battle_prompt(*info)
# print(prompt)
