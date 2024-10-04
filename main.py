import telebot
from pdf2docx import Converter
from docx2pdf import convert
from PIL import Image
import img2pdf
import os
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


# Конвертация изображения в PDF
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Привет! Я бот, который конвертирует .pdf, .word и изображения в PDF. Просто отправь ссылку или документ.')


@bot.message_handler(commands=['convert'])
def messege(message):
    bot.send_message(message.chat.id, 'Загрузите ваш документ .pdf, .word или изображение.')


@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    file_info = bot.get_file(message.document.file_id)
    file_path = file_info.file_path
    file_name = message.document.file_name
    file_extension = file_name.split('.')[-1].lower()

    # Скачиваем файл
    downloaded_file = bot.download_file(file_path)

    if file_extension == 'pdf':
        # Конвертируем PDF в DOCX
        with open('input.pdf', 'wb') as f:
            f.write(downloaded_file)
        cv = Converter('input.pdf')
        cv.convert('output.docx', start=0, end=None)
        cv.close()
        with open('output.docx', 'rb') as f:
            bot.send_document(chat_id, f)
    elif file_extension == 'docx':
        # Конвертируем DOCX в PDF
        with open('input.docx', 'wb') as f:
            f.write(downloaded_file)
        convert('input.docx', 'output.pdf')
        with open('output.pdf', 'rb') as f:
            bot.send_document(chat_id, f)
    elif file_extension in ['jpg', 'jpeg', 'png']:
        # Конвертируем изображение в PDF
        with open(f'input.{file_extension}', 'wb') as f:
            f.write(downloaded_file)

        # Создание PDF из изображения
        with open('output.pdf', 'wb') as f:
            f.write(img2pdf.convert(f'input.{file_extension}'))

        with open('output.pdf', 'rb') as f:
            bot.send_document(chat_id, f)
        os.remove(f'input.{file_extension}')  # Удаляем временный файл
    else:
        bot.send_message(chat_id, 'Извините, я могу работать только с PDF, DOCX и изображениями (JPG, PNG).')


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    # Получаем файл изображения
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохраняем изображение
    with open('input.jpg', 'wb') as f:
        f.write(downloaded_file)

    # Конвертируем изображение в PDF
    with open('output.pdf', 'wb') as f:
        f.write(img2pdf.convert('input.jpg'))

    with open('output.pdf', 'rb') as f:
        bot.send_document(chat_id, f)

    os.remove('input.jpg')  # Удаляем временный файл


def main():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == '__main__':
    main()
