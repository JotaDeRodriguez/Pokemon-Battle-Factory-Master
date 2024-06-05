from json_Reader import load_type_data
from collections import defaultdict


# Function to get type interactions in a simplified dictionary format
def get_attacking_type_interaction(attacking_type):
    type_advantages = load_type_data(
        "path/to/Gen III - Attacking Type Chart.json")

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
        "path/to/Gen III - Defending Type Chart.json")

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
