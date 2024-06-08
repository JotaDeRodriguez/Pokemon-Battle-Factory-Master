from json_Reader import load_type_data

ability_info = load_type_data("path/to/Gen III - Abilities.json")


def get_pokemon_ability(pokemon_name):

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
