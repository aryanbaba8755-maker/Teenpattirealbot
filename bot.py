import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
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

# Security & Utils
async def check_admin(update: Update):
    if update.effective_user.id != OWNER_ID:
        return False
    # Auto-leave if not in group (basic check)
    return True

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_admin(update):
        await update.message.reply_text("Bot Ready!")

async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update): return
    
    cmd = update.message.text.split()
    if len(cmd) < 2:
        await update.message.reply_text("Enter name and number (e.g., /show 1)")
        return
    
    val = cmd[1]
    suits = ['♥️', '♦️', '♠️', '♣️']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    if val.isdigit() and 1 <= int(val) <= 100:
        result = f"{val} cards: {random.choice(suits)}{random.choice(ranks)}"
        await update.message.reply_text(result)
    else:
        # Handling name/text
        await update.message.reply_text(f"Result for {val}: {random.choice(suits)}{random.choice(ranks)}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update): return
    await update.message.reply_text(str(random.randint(1, 6)))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update): return
    await update.message.reply_text(random.choice(['Stone', 'Paper', 'Scissors']))

if __name__ == '__main__':
    Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('show', show_command))
    application.add_handler(CommandHandler('roll', roll))
    application.add_handler(CommandHandler('sps', sps))
    
    application.run_polling()
