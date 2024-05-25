import os
import telebot
from PIL import Image
from rembg import remove
from telebot import types
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
IMAGES_DIR = 'images'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Just send your image! Supported formats: PNG.')

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    # Get and save image
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    file_name = f"{IMAGES_DIR}/{file_id}.png"
    
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Removing BG and sending image
    inputPath = file_name
    outputPath = f'images/removed/{file_id}.png'

    input_image = Image.open(inputPath)
    output_image = remove(input_image)  
    output_image.save(outputPath)

    # Sending the processed image
    with open(outputPath, 'rb') as img:
        bot.send_photo(message.chat.id, img)

    import time
    time.sleep(1)  

    # Removing images after sending
    os.remove(outputPath)
    os.remove(inputPath)

@bot.message_handler(func = lambda message: True)
def handle_other(message):
    if message.content_type != message.text != '/start' or message.text != '/users':
        bot.send_message(message.chat.id, 'Send the image only! Supported formats: PNG.')

bot.polling(none_stop=True)