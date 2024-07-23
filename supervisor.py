from openai import OpenAI
from dotenv import load_dotenv
import os
from os import environ
import json

load_dotenv()
api_key = os.getenv('OPENAI_KEY')
environ["OPENAI_API_KEY"] = api_key

client = OpenAI(api_key=api_key)

def flatten_messages(messages):
    """Flatten any nested lists in the messages."""
    flattened = []
    for item in messages:
        if isinstance(item, list):
            flattened.extend(flatten_messages(item))
        elif isinstance(item, dict) and all(key in item for key in ['role', 'content']):
            flattened.append(item)
    return flattened

def load_memory_from_file(file_path):
    """Load memory from a JSON file and ensure it's a flat list of message objects."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return flatten_messages(data)
    except FileNotFoundError:
        return []

def save_memory_to_file(file_path, memory_data):
    """Save memory to a JSON file."""
    try:
        with open(file_path, "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.extend(memory_data)

    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)

def supervisor(battle_info):
    memory = load_memory_from_file("battle_context/memory.json")

    messages = [
        {"role": "system", "content": """
        
        You are an AI assistant specialized in Pokémon battles. Your goal is to make strategic decisions to defeat your 
        opponent. You have extensive knowledge of Pokémon species, types, abilities, movesets, type effectiveness, 
        battle mechanics, strategies, and item effects.

        During a battle, you should:

        Analyze the current situation, including team composition, HP levels, status conditions, and field effects.
        Make informed decisions on which Pokémon to send out, which move to use, and when to use items.
        Explain your reasoning based on type advantages, potential super-effective moves, prediction of opponent's actions, and long-term strategy.
        Adapt your strategy based on new information revealed during the battle.
        Provide clear, concise responses in the format:

        Action: [Your chosen action]
        Reasoning: [Brief explanation]
        Your aim is to make optimal plays to outmaneuver and outsmart your opponent, ensuring victory in each Pokémon battle.
        When describing the action, only say whatever one is first. Dont give two consecutive actions. Be brief.
        """},
        *memory,  # Unpack the memory list directly into messages
        {"role": "user", "content": battle_info},
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages
    )

    supervisor_response = response.choices[0].message.content

    new_memory = [
        {"role": "user", "content": battle_info},
        {"role": "assistant", "content": supervisor_response}
    ]

    save_memory_to_file("battle_context/memory.json", new_memory)
    return supervisor_response
