import requests
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from config import TOKEN


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправь мне название товара, и я поищу его на маркетплейсах.')


def search_product(update: Update, context: CallbackContext) -> None:
    product_name = update.message.text

    # Поиск на Wildberries
    wildberries_url = f'https://www.wildberries.ru/search?query={product_name}'

    # Поиск на Ozon
    ozon_url = f'https://www.ozon.ru/search/?from_global=true&text={product_name}'

    # Поиск на Avito
    avito_url = f'https://www.avito.ru/?q={product_name}'

    HEADERS = {"User-Agent": UserAgent().random}

    with requests.Session() as session:
        # Поиск on Ozon
        response = session.get(ozon_url, headers=HEADERS)
        soup = BS(response.content, "html.parser")

        oz_res = soup.find("a", {"class": "widget-search-result-container iy2"})
        if oz_res:
            ozon_link = oz_res.get('href')
            ozon_photo = soup.find("img", {"class":"is8"})
            ozon_png = ozon_photo.get("src")
            ozon_price = ''.join(char for char in oz_res.find("span").text.strip() if char.isdigit())
            update.message.reply_text(f'Результаты поиска на Ozon для "{product_name}":\n\n'
                                      f'{ozon_link} - Цена: {ozon_price}')
            context.bot.send_photo(update.message.chat_id, photo=ozon_png)

        else:
            update.message.reply_text(f'Не удалось найти информацию о товаре "{product_name}" на Ozon.')

        # Поиск on Wildberries
        response = session.get(wildberries_url, headers=HEADERS)
        soup = BS(response.content, "html.parser")

        wb_res = soup.find("a", {"class": "product-card__link j-card-link j-open-full-product-card"})
        if wb_res:
            wb_link = wb_res.get('href')
            wb_photo = soup.find("img", {"class":"product-card__img"})
            wb_png = wb_photo.get("src")
            wb_price = ''.join(char for char in wb_res.find("span").text.strip() if char.isdigit())
            update.message.reply_text(f'Результаты поиска на Wildberries для "{product_name}":\n\n'
                                      f'{wb_link} - Цена: {wb_price}')
            context.bot.send_photo(update.message.chat_id, photo=wb_png)

        else:
            update.message.reply_text(f'Не удалось найти информацию о товаре "{product_name}" на Wildberries.')

        # Поиск on Avito
        response = session.get(avito_url, headers=HEADERS)
        soup = BS(response.content, "html.parser")

        avito_res = soup.find("a", {"class": "iva-item-sliderLink-uLz1v"})
        if avito_res:
            avito_link = avito_res.get('href')
            avito_photo = soup.find("img", {"class": "photo-slider-image-YqMGj"})
            avito_png = avito_photo.get("src")
            avito_price = ''.join(char for char in avito_res.find("span").text.strip() if char.isdigit())
            update.message.reply_text(f'Результаты поиска на Avito для "{product_name}":\n\n'
                                      f'{avito_link} - Цена: {avito_price}')
            context.bot.send_photo(update.message.chat_id, photo=avito_png)

        else:
            update.message.reply_text(f'Не удалось найти информацию о товаре "{product_name}" на Avito.')

def main() -> None:
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search_product))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

