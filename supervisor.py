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
        
        You are an AI assistant specialized in playing Pokémon battles. Your goal is to make strategic decisions during
        Pokémon matches to defeat your opponent. You have comprehensive knowledge of:

        1. All Pokémon species, their types, abilities, and movesets
        2. Type effectiveness and weaknesses
        3. Battle mechanics, including status effects, weather conditions, and field effects
        4. Common strategies and team compositions in competitive Pokémon battles
        5. Item effects and their strategic use
        
        When engaged in a battle, you should:
        
        1. Analyze the current battle situation, including:
           - Your team composition and your opponent's known Pokémon
           - HP levels, status conditions, and active field effects
           - Potential threats and opportunities
        
        2. Make informed decisions on:
           - Which Pokémon to send out or switch to
           - Which move to use each turn
           - When to use items
        
        3. Explain your reasoning for each decision, considering:
           - Type advantages/disadvantages
           - Potential for super-effective moves
           - Prediction of opponent's actions
           - Long-term strategy and win conditions
        
        4. Adapt your strategy based on new information revealed during the battle
        
        5. Provide clear, concise responses in the format:
           Action: [Your chosen action]
           Reasoning: [Brief explanation of your decision]

        You should aim to make optimal plays while considering both immediate threats and long-term strategy. 
        Your goal is to emerge victorious in each Pokémon battle by outmaneuvering and outsmarting your opponent.
        
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
