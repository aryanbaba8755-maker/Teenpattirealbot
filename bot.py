import logging
import random
import threading
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from flask import Flask

# Config
TOKEN = '8699525997:AAGW_yxKqpFovncJC1HEOI3qSRpZeEYrSvY'
OWNER_ID = 7007926290
RENDER_URL = "https://teenpattirealbot-7ufs.onrender.com"

# Flask (Keep-Alive)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is alive!"

def run_flask(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    while True:
        try: requests.get(RENDER_URL)
        except: pass
        time.sleep(300)

# Security & Authorization
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Check if Owner or Admin
    member = await context.bot.get_chat_member(chat_id, user_id)
    is_admin = member.status in ['creator', 'administrator']
    is_owner = (user_id == OWNER_ID)
    
    if not (is_admin or is_owner): return False

    # Auto-leave if owner not present
    try: await context.bot.get_chat_member(chat_id, OWNER_ID)
    except:
        await context.bot.leave_chat(chat_id)
        return False
    return True

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_authorized(update, context):
        await update.message.reply_text("Bot Ready!")

async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context): return
    
    cmd = context.args
    val = cmd[0] if cmd else "1"
    
    suits = ['♥️', '♦️', '♠️', '♣️']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    card = f"{random.choice(suits)}{random.choice(ranks)}"
    # Screenshot jaisa exact format
    await update.message.reply_text(f"{val} cards: {card}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context): return
    await update.message.reply_text(str(random.randint(1, 6)))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context): return
    await update.message.reply_text(random.choice(['Stone', 'Paper', 'Scissors']))

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('show', show_command))
    application.add_handler(CommandHandler('roll', roll))
    application.add_handler(CommandHandler('sps', sps))
    
    print("Bot is running perfectly...")
    application.run_polling(drop_pending_updates=True)
