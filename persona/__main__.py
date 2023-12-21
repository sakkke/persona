import os
from dotenv import load_dotenv
from .openai_client import client
from .persona import Persona

load_dotenv()

prompt = '''You are an assistant.'''

persona = Persona(client, prompt)
persona.run(os.getenv('TOKEN'))
