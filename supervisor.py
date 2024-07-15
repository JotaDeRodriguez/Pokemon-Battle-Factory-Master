from openai import OpenAI
from dotenv import load_dotenv
import os
from os import environ


load_dotenv()
api_key = os.getenv('OPENAI_KEY')
environ["OPENAI_API_KEY"] = api_key

client = OpenAI(api_key=api_key)

def supervisor(battle_info):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
            You are a pokemon battle trainer. Tasked with deciding on a move. With the info provided, your task is making
            the optimal play. 
             """
             },
            {"role": "user", "content": f"{battle_info}. Choose the most advantageous move! Also say which turn we're on please."},
        ]
    )
    return response.choices[0].message.content
