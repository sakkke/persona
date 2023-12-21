import os
from dotenv import load_dotenv
from .persona import Persona

load_dotenv()

persona = Persona()
persona.run(os.getenv('TOKEN'))
