import os
import time
from io import BytesIO
from PIL import Image
from rembg import remove
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("No TOKEN found in environment variables")

IMAGES_DIR = 'images'
REMOVED_IMAGES_DIR = f"{IMAGES_DIR}/removed"
BOT_USERNAME = '@MRxD_the_Bot'

# Ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(REMOVED_IMAGES_DIR, exist_ok=True)

# Initialize telegram.ext Application for handling both text commands and images
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Send an image to remove its background or type a command.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('How may I help you?')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('I am MrXD bot')

def handle_response(text: str) -> str:
    text = text.lower()
    if 'hello' in text:
        return 'Hey there!'
    if 'how are you' in text:
        return 'I am good!'
    if 'advance' in text:
        return 'Remember to subscribe!'
    return 'Sorry... I do not understand what you wrote'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
            await update.message.reply_text(response)
    else:
        response: str = handle_response(text)
        print('Bot:', response)
        await update.message.reply_text(response)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_id = photo_file.file_id
    file_path = f"{IMAGES_DIR}/{file_id}.png"
    
    await photo_file.download_to_drive(file_path)
    
    input_image = Image.open(file_path)
    output_image = remove(input_image)
    output_path = f"{REMOVED_IMAGES_DIR}/{file_id}.png"
    output_image.save(output_path)

    with open(output_path, 'rb') as img:
        await update.message.reply_photo(photo=InputFile(img))
    
    time.sleep(1)
    
    os.remove(output_path)
    os.remove(file_path)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    app.add_error_handler(error)
    
    print('Polling for commands and image handling....')
    app.run_polling(poll_interval=3)
