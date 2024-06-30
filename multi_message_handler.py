import asyncio
import random
import logging
from telegram import Update

logger = logging.getLogger(__name__)

class MultiMessageHandler:
    def __init__(self, bot, session_manager, anthropic_client, claude_model, system_prompt):
        self.bot = bot
        self.session_manager = session_manager
        self.anthropic_client = anthropic_client
        self.claude_model = claude_model
        self.system_prompt = system_prompt
        self.user_queues = {}

    async def handle_message(self, update: Update, context):
        user_id = update.effective_user.id
        user_message = update.message.text

        if user_id not in self.user_queues:
            self.user_queues[user_id] = asyncio.Queue()
            asyncio.create_task(self.process_user_messages(user_id))

        await self.user_queues[user_id].put(user_message)

    async def process_user_messages(self, user_id):
        messages = []
        while True:
            try:
                message = await asyncio.wait_for(self.user_queues[user_id].get(), timeout=10.0)
                messages.append(message)
                
                if random.random() < 0.7 and len(messages) < 3:
                    continue
                
                await self.process_messages(user_id, messages)
                messages = []
            except asyncio.TimeoutError:
                if messages:
                    await self.process_messages(user_id, messages)
                    messages = []

    async def process_messages(self, user_id, messages):
        combined_message = " ".join(messages)
        self.session_manager.add_message(user_id, "user", combined_message)

        history = self.session_manager.get_history(user_id)

        api_messages = []
        last_role = None
        for msg in history:
            if msg["role"] != last_role:
                api_messages.append({"role": msg["role"], "content": msg["content"]})
                last_role = msg["role"]
            else:
                api_messages[-1]["content"] += " " + msg["content"]

        try:
            response = self.anthropic_client.messages.create(
                model=self.claude_model,
                max_tokens=1000,
                system=self.system_prompt,
                messages=api_messages
            )

            bot_messages = self.split_response(response.content[0].text)

            for bot_message in bot_messages:
                self.session_manager.add_message(user_id, "assistant", bot_message)
                
                delay = random.uniform(5, 10)
                await asyncio.sleep(delay)
                
                await self.bot.send_message(chat_id=user_id, text=bot_message)

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            await self.bot.send_message(chat_id=user_id, text="Sorry, I encountered an error while processing your request.")

    def split_response(self, response, max_length=4096):
        sentences = response.split('. ')
        messages = []
        current_message = ""

        for sentence in sentences:
            if len(current_message) + len(sentence) + 2 <= max_length:
                if current_message:
                    current_message += ". "
                current_message += sentence
            else:
                if current_message:
                    messages.append(current_message + ".")
                current_message = sentence

        if current_message:
            messages.append(current_message + ".")

        return messages