import discord

class Persona(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
