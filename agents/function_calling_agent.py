import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')


def function_calling(supervisor_input):
    client = OpenAI(api_key=api_key)  # Make sure to securely manage your API key

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """You are a helpful assistant designed to output text. An agent will hand you
                    a description of a strategy to use in Pokemon, and your task is to extract the name of the recommended move and
                    return it with proper formatting. The format corresponds to the move's name but without capital letters
                    and no spaces. The thought proces might be contrived, so do your best to conclude what the best move is. 

                    Examples:

                    Input: "In this situation, using Sludge Bomb would be effective against Water types."
                    Output: "sludgebomb"

                    Input: "Given the opponent's high defense, a special attack like flamethrower would work well."
                    Output: "flamethrower"

                    Other times, if the agent's opinion is to switch, your task is responding with what switch pokemon 
                    the agent chose, with the same rule, all in lowercase, and ony the name of the pokemon.

                    Finally, sometimes the current pokemon gets fainted, the agent will reccomend what pokemon to switch into. 
                    Same deal as the switching option. 

                    never reply or add anything else. Your response must always be either a move or a pokemon's name.
                    """},

            {"role": "user", "content": supervisor_input}
        ]
    )

    if response.choices and response.choices[0].message and response.choices[0].message.content:
        recommended_move = response.choices[0].message.content.strip().lower().replace(" ", "")

        cleaned_recommended_move = re.sub(r'\W+', '', recommended_move).lower()

        return cleaned_recommended_move

    else:
        print("No valid response received.")
        return None
