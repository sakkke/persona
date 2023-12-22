import os
from dotenv import load_dotenv
from .openai_client import client
from .persona import Persona

load_dotenv()

prompt = '''Please answer SUCCINCTLY and DIRECTLY. You are an assistant.'''

persona = Persona(client, prompt, model='gpt-4-vision-preview')
persona.run(os.getenv('TOKEN'))
