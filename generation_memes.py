import telebot
from telebot import types
from tokens import TOKEN
from PIL import Image, ImageDraw, ImageFont
import os

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message: types.Message):
    bot.send_message(message.chat.id, 'отправьте картинку чтобы начать')


@bot.message_handler(content_types=['photo'])
def handle_photo(message: types.Message):
    # file id
    file_id = message.photo[-1].file_id
    # path to file
    file_path = bot.get_file(file_id).file_path
    # download
    downloaded_file = bot.download_file(file_path)
    with open(f'pics\\{message.chat.id}.jpg', "wb") as pic:
        pic.write(downloaded_file)
    # ПРОСИМ ВВЕСТИ ВЕРХНИЙ ТЕКСТ
    bot.send_message(message.chat.id, 'отправьте верхний текст')
    bot.register_next_step_handler_by_chat_id(message.chat.id, handle_toptext)


def attribute_error_handler(func):
    def wrapper(message, *args, **kwargs):
        try:
            func(message, *args, **kwargs)
        except AttributeError:
            bot.send_message(message.chat.id, 'можно ввести только текст')
            bot.register_next_step_handler_by_chat_id(message.chat.id, wrapper,*args, **kwargs )
    return wrapper


@attribute_error_handler
def handle_toptext(message: types.Message):
    top_text = message.text.upper()
    # просим ввести нижний текст
    bot.send_message(message.chat.id, 'отправьте нижний текст')
    bot.register_next_step_handler_by_chat_id(message.chat.id, handle_bottomtext, top_text)


@attribute_error_handler
def handle_bottomtext(message: types.Message, top_text: str):
    bottom_text = message.text.upper()
    bot.send_message(message.chat.id, 'выберите размер шрифта')
    bot.register_next_step_handler_by_chat_id(message.chat.id, handle_textsize, top_text, bottom_text)


@attribute_error_handler
def handle_textsize(message: types.Message, top_text: str, bottom_text: str):
    try:
        size = int(message.text.lower())

        send_meme(message.chat.id, top_text, bottom_text, size)
    except ValueError:
        bot.send_message(message.chat.id, 'можно ввести только число')
        bot.register_next_step_handler_by_chat_id(message.chat.id, handle_textsize, top_text, bottom_text)


def generate_meme(chat_id: int, top_text: str, bottom_text: str, size: int):
    image = Image.open(f'pics\\{chat_id}.jpg')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('impact.ttf', size=size)
    # ширина текста
    text1 = draw.textbbox((0, 0), top_text, font=font)
    text1_width = text1[2]

    draw.text(((image.size[0] - text1_width) / 2, 10), top_text, font=font, fill='white')

    text2 = draw.textbbox((0, 0), bottom_text, font=font)
    text2_width = text2[2]
    text2_height = text2[3]

    draw.text(((image.size[0] - text2_width) / 2, image.size[1] - text2_height - 10), bottom_text, font=font,
              fill='white')

    image.save(f'pics\\temp_{chat_id}.jpg')


def send_meme(chat_id: int, top_text: str, bottom_text: str, size: int):
    generate_meme(chat_id, top_text, bottom_text, size)

    with open(f'pics\\temp_{chat_id}.jpg', 'rb') as pic:
        bot.send_photo(chat_id, pic)

    os.remove(f'pics\\temp_{chat_id}.jpg')
    os.remove(f'pics\\{chat_id}.jpg')


if __name__ == '__main__':
    bot.polling(none_stop=True)
