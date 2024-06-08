from dotenv import load_dotenv
load_dotenv()

import openai
from openai import OpenAI
import ast

client = OpenAI()


system_prompt = '''
    You are an agent specialized in identifying Pokemon in the game Pokemon Emerald. When given a screenshot of the game's combat, you'll identify
    what pokemon is the enemy using, as well as what are the attacking moves for the user, based of the text information the game provides.
    You must reply only with the name of the pokemon, and list the moves available. 
    Return keywords in the format of an list of strings, like this:
    ["Rhydon", "Quick Attack", "Tail Whip", "Earthquake", "Scratch"]
'''

def read_screenshot(image):

    image = image

    response = openai.chat.completions.create(
      model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                          "image_url": {
                            "url": image}
                    },
                ],
            },
        ],
      max_tokens=300,

    )

    response_list = ast.literal_eval(response.choices[0].message.content)
    return response_list
