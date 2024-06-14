from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain import hub

from read_screenshot import read_screenshot
from get_type_interaction import natural_language_typing_dynamics
from get_pokemon_type import get_pokemon_type
from get_moves_info import get_moves_info
from get_abilities import get_pokemon_ability

def aggressive_agent(image):

    load_dotenv()

    # Pull the prompt using LangChain hub
    prompt = hub.pull("jotaderodriguez/aggressive_pokemon_agent")

    # Initialize LangChain with OpenAI API
    client = ChatOpenAI()
    llm = ChatOpenAI(model_name="gpt-4o")
    llm_chain = prompt | llm

    # Read information from the screenshot
    try:
        screenshot_info = read_screenshot(image)
        rival_pokemon = screenshot_info[0]
        rival_ability = get_pokemon_ability(rival_pokemon)
        current_pokemon_moves = screenshot_info[1:4]

        # Get Pokemon types and dynamics
        pokemon_to_type = get_pokemon_type(rival_pokemon)
        typing = pokemon_to_type.get(rival_pokemon)
        type_dynamics = natural_language_typing_dynamics(typing)

        # Collect information about the moves
        move_list = []
        for move in current_pokemon_moves:
            move_info = get_moves_info(move)
            move_list.append(move_info)

        # Formulate the question for the LangChain
        question = {
            "rival_pokemon": rival_pokemon,
            "ability": rival_ability,
            "typing": typing,
            "move_list": move_list,
            "type_dynamics": type_dynamics
        }

        # Invoke the LangChain with the formulated question
        result = llm_chain.invoke(question)
        return "Response from the bot: " + str(result)

    except Exception as e:
        return "Error when analyzing Pokemon battle: " + str(e)