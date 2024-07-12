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
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a pokemon battles supervisor, tasked with advising on battles"
             },
            {"role": "user", "content": f"{battle_info}. Tell me whats going on, summarize the battle"},
        ]
    )
    return response.choices[0].message.content
