import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from anthropic import Anthropic
from config import TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT
from user_session_manager import UserSessionManager
from multi_message_handler import MultiMessageHandler

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

async def start(update: Update, context):
    await update.message.reply_text("Hello! I'm a bot that can answer programming questions. How can I help you?")

def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Create instances of UserSessionManager and MultiMessageHandler
    session_manager = UserSessionManager()
    multi_message_handler = MultiMessageHandler(application.bot, session_manager, anthropic, CLAUDE_MODEL, SYSTEM_PROMPT)

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, multi_message_handler.handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()