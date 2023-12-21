import os
from dotenv import load_dotenv
from .openai_client import client
from .persona import Persona

load_dotenv()

persona = Persona(client, 'You are an assistant.')
persona.run(os.getenv('TOKEN'))
