import os
import json
from dotenv import load_dotenv

from openai import OpenAI
from langchain_openai import ChatOpenAI
import openai


# set the LANGCHAIN_API_KEY environment variable (create key in settings)
from langchain import hub
prompt = hub.pull("jotaderodriguez/aggressive_pokemon_agent")

from Information_sources.get_type_interaction import natural_language_typing_dynamics
from Information_sources.get_pokemon_type import get_pokemon_type
from Information_sources.get_moves_info import describe_move, move_to_id
from Information_sources.get_abilities import get_pokemon_ability

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')


def aggressive_move(current_pokemon_and_moves):


    # Pull the prompt using LangChain hub
    prompt = hub.pull("jotaderodriguez/aggressive_pokemon_agent")

    # Initialize LangChain with OpenAI API
    client = ChatOpenAI()
    llm = ChatOpenAI(model_name="gpt-4o")
    llm_chain = prompt | llm

    # Read information from the screenshot
    try:
        current_pokemon = current_pokemon_and_moves[0]
        rival_pokemon = current_pokemon_and_moves[1]
        current_pokemon_moves = current_pokemon_and_moves[2]
        ability = get_pokemon_ability(rival_pokemon)
        pokemon_typing = get_pokemon_type(rival_pokemon)
        typing = pokemon_typing.get(rival_pokemon)
        type_dynamics = natural_language_typing_dynamics(typing)

        move_list = current_pokemon_moves

        moves_info = []

        for move in move_list:
            move_info = describe_move(move)
            moves_info.append(move_info)

        question = {
            "rival_pokemon": rival_pokemon,
            "ability": ability,
            "typing": pokemon_typing,
            "move_list": moves_info,
            "type_dynamics": type_dynamics
        }

        # Invoke the LangChain with the formulated question
        result = llm_chain.invoke(question)

        return result.content

    except Exception as e:
        return "Error when analyzing Pokemon battle: " + str(e)
