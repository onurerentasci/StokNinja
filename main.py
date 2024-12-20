import logging
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Final, Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN: Final = os.getenv('TELEGRAM_TOKEN')
BOT_USERNAME: Final = os.getenv('BOT_USERNAME')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

product_links: Dict[str, dict] = {}

WEBSITE_SELECTORS = {
    "trendyol": {
        "out_of_stock": ('section', {'class': 'out-of-stock'}),
        "in_stock": ('button', {'class': 'buy-now-button'}),  
    },
}


def get_website_name(url: str) -> str:
    domain = urlparse(url).netloc.lower()
    if any(site in domain for site in ['trendyol', 'trendyolmilla']):
        return 'trendyol'
    elif 'telegramtestpage.vercel.app' in domain:
        return 'testpage'
    # elif 'zara' in domain:
    #     return 'zara'
    # elif 'pullandbear' in domain:
    #     return 'pullandbear'
    # elif 'bershka' in domain:
    #     return 'bershka'
    else:
        return 'unknown'


async def check_stock(url: str) -> str:
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            website = get_website_name(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            logging.info(f"URL: {url}")
            logging.info(f"Website: {website}")
            
            if website in ['trendyol', 'trendyoMilla', 'testpage']:
                product_container = soup.find('div', class_='product-button-container')
                if product_container:
                    buy_now_button = product_container.find('a', class_='buy-now-button')
                    notify_me_button = product_container.find('button', class_='notify-me-btn')
                    
                    logging.info(f"Buy Now Button: {bool(buy_now_button)}")
                    logging.info(f"Notify Me Button: {bool(notify_me_button)}")
                    
                    if notify_me_button:
                        return 'Şuan stok yok. Ninja senin için stok durumunu izlemeye başladı! 🥷🛒'
                    elif buy_now_button:
                        return 'Stokta var'
                return 'Şuan stok yok. Ninja senin için stok durumunu izlemeye başladı! 🥷🛒'

            return 'Site desteklenmiyor'

    except Exception as e:
        logging.error(f"Hata oluştu: {str(e)}", exc_info=True)
        return f'Hata oluştu: {str(e)}'

async def periodic_stock_check(context: ContextTypes.DEFAULT_TYPE):
    if not product_links:
        logging.info("Takip listesi boş olduğu için stok kontrolü atlanıyor.")
        return
        
    logging.info(f"Stok kontrolü başlatılıyor. Takip edilen ürün sayısı: {len(product_links)}")
    for url, info in product_links.items():
        try:
            current_status = await check_stock(url)
            if info['last_status'] != current_status:
                await context.bot.send_message(
                    chat_id=info['chat_id'],
                    text=f"🔔 Stok durumu değişti!\nÜrün: {url}\nYeni durum: {current_status}"
                )
                product_links[url]['last_status'] = current_status
        except Exception as e:
            logging.error(f"Error checking {url}: {str(e)}")
        await asyncio.sleep(1)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Merhaba! Ben StokNinja 🥷🛒 \nBana bir ürün linki gönder, hemen stokta mı değil mi söyleyeyim. 🚀\n\n"
        "Komutlar:\n"
        "/start - Botu başlat\n"
        "/list - Takip edilen ürünleri listele\n"
        "/remove <numara> - Listeden ürün kaldır"
    )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_links = [url for url, info in product_links.items() if info['chat_id'] == chat_id]

    if not user_links:
        await update.message.reply_text("Takip ettiğiniz ürün bulunmamaktadır.")
        return

    message = "📋 Takip ettiğiniz ürünler:\n\n"
    for i, url in enumerate(user_links, 1):
        status = product_links[url]['last_status']
        message += f"{i}. {url}\nDurum: {status}\n\n"

    await update.message.reply_text(message)


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_links = [url for url, info in product_links.items() if info['chat_id'] == chat_id]

    if not user_links:
        await update.message.reply_text("Takip ettiğiniz ürün bulunmamaktadır.")
        return

    try:
        if not context.args:
            await update.message.reply_text("Lütfen kaldırmak istediğiniz ürünün numarasını girin.\nÖrnek: /remove 1")
            return

        index = int(context.args[0]) - 1

        if index < 0 or index >= len(user_links):
            await update.message.reply_text(f"Geçersiz numara. Lütfen 1 ile {len(user_links)} arasında bir numara girin.")
            return

        url_to_remove = user_links[index]
        del product_links[url_to_remove]

        await update.message.reply_text(f"✅ Ürün takip listesinden kaldırıldı:\n{url_to_remove}")

    except ValueError:
        await update.message.reply_text("Lütfen geçerli bir numara girin.\nÖrnek: /remove 1")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    chat_id = update.effective_chat.id

    if 'http' in text.lower():
        response = await check_stock(text)
        product_links[text] = {
            'chat_id': chat_id,
            'last_status': response,
            'added_at': datetime.now(timezone.utc)
        }
        await update.message.reply_text(
            f"🔍 Ürün takibe alındı!\n\n"
            f"{response}\n"
        )
    else:
        await update.message.reply_text("Lütfen geçerli bir ürün linki gönderin.")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('list', list_command))
    app.add_handler(CommandHandler('remove', remove_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    job_queue = app.job_queue
    job_queue.run_repeating(periodic_stock_check, interval=900, first=10)

    logging.info('Bot başlatıldı...')
    app.run_polling(poll_interval=3)


if __name__ == '__main__':
    main()