from json_Reader import load_type_data


def get_moves_info(move):
    moves_data = load_type_data(
        r"C:\Users\juandavid.rodriguez\Documents\Langchain\PokemonProject\Gen III - Move List.json")

    if move in moves_data:
        move_info = moves_data[move]
        move_info = {
            move: [
                {"effect": move_info.get("Effect", "No effect info available")},
                {"type": move_info.get("Type", "No type info available")},
                {"pp": move_info.get("PP", "No PP info available")},
                {"power": move_info.get("Power", "No power info available")},
                {"accuracy": move_info.get("Accuracy", "No accuracy info available")}
            ]
        }
    else:
        move_info = {move: "Move not found"}

    return move_info
