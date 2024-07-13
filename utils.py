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

    ability_info = load_type_data("information/Gen III - Abilities.json")

    ability_list = []

    for ability in ability_info:
        description = ability_info[ability]['Description']
        learnt_by = ability_info[ability]['Learnt By']

        if pokemon_name in learnt_by:
            full_description = str(ability + ":" + " " + description)
            ability_list.append(full_description)

    if len(ability_list)>1:
        string = "The pokemon can have one of two possible abilities:"
        string_list = str(string + " " + str(ability_list))
        return string_list
    else:
        return ability_list


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
    type_advantages = load_type_data(
        r"C:\Users\juandavid.rodriguez\Documents\Langchain\PokemonProject\Gen III - Attacking Type Chart.json")

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
    type_advantages = load_type_data(
        r"C:\Users\juandavid.rodriguez\Documents\Langchain\PokemonProject\Gen III - Defending Type Chart.json")

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


def natural_language_typing_dynamics(typing):

    type_interactions = get_combined_type_interaction(typing)

    parts = []
    if type_interactions.get('four times effective'):
        parts.append(f"The pokemon is four times weak to {', '.join(type_interactions['four times effective'])}.")
    if type_interactions.get('super effective'):
        parts.append(f"Weak to {', '.join(type_interactions['super effective'])}.")
    if type_interactions.get('not very effective'):
        parts.append(f"Resistant to {', '.join(type_interactions['not very effective'])}.")
    if type_interactions.get('almost ineffective'):
        parts.append(f"Heavily resistant to {', '.join(type_interactions['almost ineffective'])}.")
    if type_interactions.get('no effect'):
        parts.append(f"And moves of {', '.join(type_interactions['no effect'])} type will not have any effect at all.")
    if type_interactions.get('normal damage'):
        parts.append(f"Moves of types {', '.join(type_interactions['normal damage'])}. will make normal damage")

    statement = '\n'.join(parts)
    return statement

def prompt_builder(info):

    rival_pokemon = info[1]

    get_type = get_pokemon_type(rival_pokemon)
    rival_typing = get_type[rival_pokemon]

    rival_type_dynamics = natural_language_typing_dynamics(rival_typing)

    pokemon = info[0]

    get_type = get_pokemon_type(pokemon)
    own_typing = get_type[pokemon]

    type_dynamics = natural_language_typing_dynamics(own_typing)

    remaining_pokemon = info[3]

    remaining_pokemon_and_typing = ""

    for benched_pokemon in remaining_pokemon:
        get_type = get_pokemon_type(benched_pokemon)
        individual_typing = get_type[benched_pokemon]  # Assuming this returns a list of types like ['Poison']
        typing_str = ', '.join(individual_typing)  # Join all types into a single string separated by commas
        remaining_pokemon_and_typing += f"{benched_pokemon} ({typing_str}), "

    prompt = f"""You are facing {rival_pokemon}. It's typing is {rival_typing}.

    It's likely to attack with moves of its type.

    Your Pokemon is {pokemon}, of type {own_typing}

    Your own type dynamics go as follow: {type_dynamics}

    Your remaining pokemon and their types are:
    {remaining_pokemon_and_typing}. They have moves of their own types, so make use of type advantages.

    Here's the rival type dynamics:
    {rival_type_dynamics}


    Be concise and use only the information provided"""

