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
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# --- 3. COMMAND HANDLERS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Galti: /show 1")
        return

    user_num = context.args[0]
    selected_cards = random.sample(DECK, 3)
    
    # Cards ko ek hi message mein bhejna behtar hai
    cards_text = " ".join(selected_cards)
    await update.message.reply_text(f"Show ka no: {user_num}\nCards: {cards_text}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = random.choice([1, 2, 3, 4, 5, 6])
    await update.message.reply_text(str(res))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = random.choice(["Stone", "Paper", "Scissors"])
    await update.message.reply_text(res)

# --- 4. MAIN ---
if __name__ == '__main__':
    keep_alive()
    
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    
    print("🚀 Bot Started!")
    application.run_polling(drop_pending_updates=True)
