import discord
from openai import OpenAI
from typing import List, Optional, TypedDict
from .utils import removeprefix

class Message:
    content: str
    role: str

class Persona(discord.Client):
    assistant = 'Please answer DO NOT include `^<@\d+>: `.'
    max_tokens: int
    model: str
    openai_client: OpenAI

    def __init__(self, openai_client: OpenAI, first_message: str,
                 max_tokens: Optional[int] = 1000, model: Optional[str] = 'gpt-3.5-turbo',
                 *args, **kwargs):
        self.openai_client = openai_client
        self.first_message = first_message
        self.max_tokens = max_tokens
        self.model = model
        super(Persona, self).__init__(*args, **kwargs)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message: discord.Message):
        is_mention = message.content.startswith(self.build_message_prefix())
        is_reference = message.reference is not None
        is_my_reference = False
        if is_reference:
            referenced_message = await message.channel.fetch_message(
                message.reference.message_id)
            if referenced_message.author == self.user:
                is_my_reference = True
        if is_mention or is_my_reference:
            messages = await self.build_messages(message, [])
            print(messages)
            completion = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
            )
            await message.reply(completion.choices[0].message.content)

    def build_assistant(self) -> Message:
        return {'role': 'system', 'content': self.assistant}

    def build_instructions(self) -> Message:
        return {'role': 'system', 'content': self.first_message}

    def build_message(self, message: discord.Message) -> Message:
        role = ''
        is_myself = message.author == self.user
        if is_myself:
            role = 'system'
        else:
            role = 'user'
        mention = message.author.mention
        content = removeprefix(message.content, self.build_message_prefix())
        to_use_gpt_4_vision_preview = self.model == 'gpt-4-vision-preview'
        if to_use_gpt_4_vision_preview:
            supported_exts = [
                '.gif',
                '.jpeg',
                '.jpg',
                '.png',
            ]
            images = []
            for attachment in message.attachments:
                for supported_ext in supported_exts:
                    if attachment.filename.endswith(supported_ext):
                        images.append(
                            {'type': 'image_url', 'image_url': attachment.url},
                        )
                        break
            return {
                'role': role,
                'content': [
                    {'type': 'text', 'text': f'{mention}: {content}'},
                ] + images,
            }
        else:
            return {'role': role, 'content': f'{mention}: {content}'}

    async def build_messages(
            self,
            message: discord.Message,
            messages: List[Message]) -> List[Message]:
        is_reference = message.reference is not None
        if not messages:
            messages.insert(0, self.build_assistant())
            messages.insert(0, self.build_message(message))
        if is_reference:
            referenced_message = await message.channel.fetch_message(
                message.reference.message_id)
            messages.insert(0, self.build_message(message))
            messages.insert(0, self.build_message(referenced_message))
            return await self.build_messages(referenced_message, messages)
        if messages:
            messages.insert(0, self.build_instructions())
            return messages
        return await self.build_messages(message, messages)

    def build_message_prefix(self) -> str:
        return f'{self.user.mention} '
