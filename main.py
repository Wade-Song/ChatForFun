import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from anthropic import Anthropic
from config import TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

async def start(update: Update, context):
    await update.message.reply_text("Hello! I'm a bot that can answer programming questions. How can I help you?")

async def handle_message(update: Update, context):
    user_message = update.message.text
    
    # Call Claude API
    try:
        response = anthropic.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # Send Claude's response back to the user
        await update.message.reply_text(response.content[0].text)
    except Exception as e:
        logger.error(f"Error calling Claude API: {e}")
        await update.message.reply_text("Sorry, I encountered an error while processing your request.")

def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()