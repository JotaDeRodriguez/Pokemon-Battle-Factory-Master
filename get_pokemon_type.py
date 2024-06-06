from json_Reader import load_type_data

pokemon_type = load_type_data("path/to/Gen III - Clean_Pokemon_List")


def get_pokemon_type(pokemon_name):

    type_info = {}

    for pokemon in pokemon_type:
        if pokemon["Pokemon Name"].lower() == pokemon_name.lower():  # Case insensitive comparison
            types = [pokemon["Type"]]
            if pokemon.get("Type2"):
                types.append(pokemon["Type2"])

            type_info[pokemon_name] = types
            break

    return type_info
