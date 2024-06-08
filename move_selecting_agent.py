from dotenv import load_dotenv

from langchain_openai import OpenAI
from langchain import hub

from get_type_interaction import natural_language_typing_dynamics
from get_pokemon_type import get_pokemon_type
from get_moves_info import get_moves_info

from Read_Screenshot import read_screenshot

load_dotenv()

# Pull the prompt using LangChain hub
prompt = hub.pull("jotaderodriguez/pokemon_prompt")

# Initialize LangChain with OpenAI API
client = OpenAI()
llm = OpenAI()

llm_chain = prompt | llm


screenshot_info = read_screenshot(r"https://i.imgur.com/U2wdHnQ.png")
rival_pokemon = screenshot_info[0]

current_pokemon_moves = screenshot_info[1:5]

pokemon_to_type = get_pokemon_type(rival_pokemon)
typing = pokemon_to_type.get(rival_pokemon)

type_dynamics = natural_language_typing_dynamics(typing)

print(type_dynamics)

move_list = []

for move in current_pokemon_moves:
    move_info = get_moves_info(move)
    move_list.append(move_info)


question = {
    "rival_pokemon": rival_pokemon,
    "typing": typing,
    "move_list": move_list,
    "type_dynamics": type_dynamics
    }

try:
    result = llm_chain.invoke(question)
    print("Response from the bot:", result)
except Exception as e:
    print("Error when invoking LangChain:", str(e))
