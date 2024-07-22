import json
from typing import List, Dict

# Assuming these utility functions are defined in a separate file
from utils import load_type_data, get_moves_info, get_ability_description, get_ability_name


def load_team_data(file_path: str) -> Dict:
    """Load team data from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def format_move_info(move: Dict) -> str:
    """Format information about a single move."""
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

    base_info = f"{move_name}: A {move_type}-type move. Power {move_power}. {move_effect}"

    if pp < 5:
        return f"{base_info} It only has {pp} power points left."

    return base_info


def format_pokemon_info(pokemon: Dict) -> str:
    """Format information about a single Pokémon."""
    species = pokemon['ident'].split(': ')[1]
    condition = pokemon['condition']

    if condition == "0 fnt":
        return f"{species} is fainted, and unable to battle."

    hp_percentage = f"{(eval(condition) * 100):.2f}%"
    ability_name = get_ability_name(pokemon["baseAbility"])
    ability_description = get_ability_description(pokemon["baseAbility"])

    return f"{species} with {hp_percentage} HP remaining.\n" \
           f"Its ability is {ability_name}: {ability_description}"


def build_battle_prompt(current_pokemon: str, opposing_pokemon: str) -> str:
    """Build a comprehensive battle prompt based on the current team situation."""
    team_data = load_team_data('battle_context/team_info.json')

    prompt_parts = [
        f"You're facing {opposing_pokemon}. Your current pokemon is {current_pokemon}.",
        "\nYour active Pokémon's moves are:"
    ]

    # Format active Pokémon's moves
    for pokemon in team_data['active']:
        prompt_parts.extend(format_move_info(move) for move in pokemon['moves'])

    prompt_parts.append("\nIn your bench sit:")

    # Format bench Pokémon information
    for pokemon in (p for p in team_data['side']['pokemon'] if not p["active"]):
        prompt_parts.append(format_pokemon_info(pokemon))

    return '\n'.join(prompt_parts)


# Example usage
if __name__ == "__main__":
    prompt = build_battle_prompt("Swampert", "Blaziken")
    print(prompt)