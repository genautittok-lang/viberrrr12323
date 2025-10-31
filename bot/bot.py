# bot.py - MEGA INVITER PRO для CryptoVibeTop1
import asyncio
import json
import re
import logging
import os
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import schedule
import threading
import time as time_module

# === НАЛАШТУВАННЯ З ENV ===
TOKEN = os.getenv("TOKEN", "8057519002:AAHwyBqMtVf1u5LhGtx47vZFygD46Ydm0TQ")
GROUP_USERNAME = "Mir_znakomctva"  # без @
CHANNEL_LINK = "https://t.me/CryptoVibetop1"
BOT_USERNAME = "CryptoVibeBot"  # твій бот

# === БАЗА ДАНИХ ===
COLLECTED_FILE = "data/collected.json"
SENT_FILE = "data/sent.json"
SUBSCRIBERS_FILE = "data/subscribers.json"

def load_json(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except:
        return set()

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(list(data), f, ensure_ascii=False, indent=2)

collected = load_json(COLLECTED_FILE)
sent = load_json(SENT_FILE)
subscribers = load_json(SUBSCRIBERS_FILE)  # ID тих, хто в розсилці

bot = Bot(token=TOKEN)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# === ЗБИРАННЯ @username ===
async def collect_from_comments(update, context):
    msg = update.message
    if not msg.chat.username or msg.chat.username.lower() != GROUP_USERNAME.lower():
        return
    
    usernames = re.findall(r'@[\w]+', msg.text or "")
    for username in usernames:
        clean = username.lower()
        if clean != f"@{GROUP_USERNAME}".lower() and clean not in collected:
            collected.add(clean)
            save_json(COLLECTED_FILE, collected)
            logging.info(f"Зібрано: {clean}")
            await send_invite_to_username(clean)

# === НАДСИЛАННЯ В ПРИВАТ ===
async def send_invite_to_username(username):
    if username in sent:
        return
    
    keyboard = [
        [InlineKeyboardButton("ПРИЄДНАТИСЯ ДО CryptoVibeTop1", url=CHANNEL_LINK)],
        [InlineKeyboardButton("Отримати сигнали", url=f"https://t.me/{BOT_USERNAME}")],
        [InlineKeyboardButton("Відписатися", callback_data=f"unsub_{username}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        f"Привіт, {username}! \n\n"
        "Топові сигнали по крипті: +100%, +300%, +500%\n"
        "Реальні кейси, аналітика, інсайди\n\n"
        "Заходь — і ти в грі! "
    )
    
    try:
        await bot.send_message(
            chat_id=username,
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        sent.add(username)
        save_json(SENT_FILE, sent)
        logging.info(f"Запрошення надіслано: {username}")
        await asyncio.sleep(2)
    except Exception as e:
        logging.warning(f"Не вдалося {username}: {e}")

# === ЩОДЕННА РОЗСИЛКА ПО ПІДПИСНИКАХ ===
async def daily_broadcast():
    if not subscribers:
        return
    text = (
        "*CryptoVibeTop1 — твій профіт сьогодні!*\n\n"
        "Новий сигнал: *BTC → $75k*\n"
        "Альти: *SOL, TON, XRP*\n\n"
        "Тисни кнопку — і в каналі! "
    )
    keyboard = [[InlineKeyboardButton("У КАНАЛ", url=CHANNEL_LINK)]]
    for user_id in list(subscribers)[:30]:  # ліміт
        try:
            await bot.send_message(user_id, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            await asyncio.sleep(1)
        except:
            pass

# === КОМАНДИ ===
async def start(update, context):
    user_id = update.effective_user.id
    if user_id not in subscribers:
        subscribers.add(user_id)
        save_json(SUBSCRIBERS_FILE, subscribers)
    await update.message.reply_text("Ти в розсилці! Очікуй сигнали ")

# === ЗАПУСК РОЗСИЛКИ ===
def run_broadcast():
    asyncio.run(daily_broadcast())

schedule.every().day.at("10:00").do(run_broadcast)
schedule.every().day.at("18:00").do(run_broadcast)

def scheduler_thread():
    while True:
        schedule.run_pending()
        time_module.sleep(60)
# === ЗАПУСК БОТА ===
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.Chat(username=GROUP_USERNAME) & filters.TEXT, collect_from_comments))
application.add_handler(CommandHandler("start", start))

# Запуск планувальника
threading.Thread(target=scheduler_thread, daemon=True).start()

print("MEGA INVITER PRO ЗАПУЩЕНО!")
print("Збирає з @Mir_znakomctva → пише в приват → розсилає щодня")
application.run_polling()
