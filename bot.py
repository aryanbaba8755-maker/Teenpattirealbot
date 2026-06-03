import random
import logging
import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- 1. FLASK SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online 24/7!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. CONFIG ---
logging.basicConfig(level=logging.INFO)
OWNER_ID = 7007926290
# Aapka token yahan daal diya hai
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# --- 3. COMMAND HANDLERS ---
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not context.args:
        await update.message.reply_text("❗ Galti: /show [number]")
        return
    user_num = context.args[0]
    selected_cards = random.sample(DECK, 3)
    for card in selected_cards:
        await update.message.reply_text(f"{user_num} cards: {card}")
        await asyncio.sleep(0.05)

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await update.message.reply_text(str(random.choice([1, 3, 5])))

# --- 4. MAIN ---
if __name__ == '__main__':
    keep_alive()
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    print("🚀 Bot Started!")
    application.run_polling(drop_pending_updates=True)
