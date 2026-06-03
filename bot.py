import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from flask import Flask
from threading import Thread

# Config
TOKEN = '8699525997:AAGW_yxKqpFovncJC1HEOI3qSRpZeEYrSvY'
OWNER_ID = 7007926290

# Flask for keeping alive
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is alive!"

def run_flask(): app.run(host='0.0.0.0', port=8080)

# Security
async def is_owner(update: Update):
    return update.effective_user.id == OWNER_ID

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_owner(update):
        await update.message.reply_text("Bot Ready and listening!")

async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update): return
    
    cmd = context.args # Behtar tareeka arguments lene ka
    if not cmd:
        await update.message.reply_text("Enter name or number (e.g., /show 1)")
        return
    
    val = cmd[0]
    suits = ['♥️', '♦️', '♠️', '♣️']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    result = f"{random.choice(suits)}{random.choice(ranks)}"
    await update.message.reply_text(f"Result for {val}: {result}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update): return
    await update.message.reply_text(str(random.randint(1, 6)))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update): return
    await update.message.reply_text(random.choice(['Stone', 'Paper', 'Scissors']))

if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('show', show_command))
    application.add_handler(CommandHandler('roll', roll))
    application.add_handler(CommandHandler('sps', sps))
    
    # SABSE ZAROORI: drop_pending_updates=True
    print("Bot is starting...")
    application.run_polling(drop_pending_updates=True)
