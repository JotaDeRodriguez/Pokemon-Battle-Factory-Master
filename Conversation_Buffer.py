import os
import json
from dotenv import load_dotenv
from os import environ
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
# set the LANGCHAIN_API_KEY environment variable (create key in settings)
from langchain import hub
prompt = hub.pull("jotaderodriguez/supervisor-with-memory")

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_KEY')
environ["OPENAI_API_KEY"] = api_key

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
    return [{'type': 'HumanMessage' if 'HumanMessage' in str(type(msg)) else 'AIMessage', 'content': msg.content} for msg in messages]

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
    ("system", "You're an assistant who's good at Pokemon Battles. Use the following conversation history to provide context to your responses:\n\n{history}"),
    ("human", "{input}")
])

# Set up the conversation chain
conversation_with_summary = ConversationChain(
    llm=ChatOpenAI(model='gpt-3.5-turbo', temperature=0),
    memory=memory,
    prompt=prompt,
    verbose=False
)

# Continuous interaction loop
try:
    while True:
        user_input = input("Message the bot: ")
        response = conversation_with_summary.predict(input=user_input)
        print(response)
        # Update memory and serialize
        chat_memory = memory.load_memory_variables({})
        serialized_chat_memory = serialize_messages(chat_memory['history'])
        save_memory_to_file(memory_path, serialized_chat_memory)
except KeyboardInterrupt:
    print("Stopping the bot.")
