import os
import json
from dotenv import load_dotenv
from os import environ
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_KEY')
environ["OPENAI_API_KEY"] = api_key

# Initialize OpenAI client
client = OpenAI(api_key=api_key)


def load_memory_from_file(file_path):
    """Load memory from a JSON file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else data.get('history', [])
    except FileNotFoundError:
        return []


def save_memory_to_file(file_path, memory_data):
    """Save memory to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(memory_data, file)


def serialize_messages(messages):
    """Convert message objects to a serializable format."""
    return [{'type': 'HumanMessage' if 'HumanMessage' in str(type(msg)) else 'AIMessage', 'content': msg.content} for
            msg in messages]


def supervisor(battle_info, chat_history):
    history_str = "\n".join([f"{msg['type']}: {msg['content']}" for msg in chat_history])
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """
            You are a pokemon battle trainer. Tasked with deciding on a move. With the info provided, your task is making
            the optimal play. Consider the battle history when making your decision.
             """
             },
            {"role": "user",
             "content": f"Battle History:\n{history_str}\n\nCurrent Battle Info: {battle_info}\nChoose the most advantageous move!"},
        ]
    )
    return response.choices[0].message.content


# Initialize memory with specified settings
memory = ConversationBufferWindowMemory(k=3, return_messages=True)
memory_path = "battle_context/memory.json"
chat_history = load_memory_from_file(memory_path)

# Load initial memory state if available
for message in chat_history:
    if message['content']:
        if message['type'] == 'HumanMessage':
            memory.save_context({"input": message['content']}, {"output": ""})
        elif message['type'] == 'AIMessage':
            memory.save_context({"input": ""}, {"output": message['content']})

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You're an assistant who's good at Pokemon Battles. Use the following conversation history to provide context to your responses:\n\n{history}"),
    ("human", "{input}")
])

# Set up the conversation chain
conversation_with_summary = ConversationChain(
    llm=ChatOpenAI(model='gpt-3.5-turbo', temperature=0),
    memory=memory,
    prompt=prompt,
    verbose=False
)


def process_battle(battle_info):
    # First, use the conversation chain to process the battle info
    conversation_response = conversation_with_summary.predict(input=battle_info)

    # Then, use the supervisor to make a decision
    chat_memory = memory.load_memory_variables({})
    serialized_chat_memory = serialize_messages(chat_memory['history'])
    supervisor_decision = supervisor(battle_info, serialized_chat_memory)

    # Update memory and save
    memory.save_context({"input": battle_info}, {"output": supervisor_decision})
    chat_memory = memory.load_memory_variables({})
    serialized_chat_memory = serialize_messages(chat_memory['history'])
    save_memory_to_file(memory_path, serialized_chat_memory)

    return conversation_response, supervisor_decision


# Example usage
battle_info = "Pikachu used thunderbolt! The attack was supereffective. Gyarados fainted. Rival sent out Rhydon."
conversation_response, supervisor_decision = process_battle(battle_info)

print("Conversation Response:", conversation_response)
print("\nSupervisor Decision:", supervisor_decision)