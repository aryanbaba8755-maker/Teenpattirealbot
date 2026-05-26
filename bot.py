import random
import logging
import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- 1. FLASK SERVER (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home(): 
    return "Bot is Online 24/7!"

def run():
    # Render automatic PORT environment variable deta hai, default 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. CONFIG ---
logging.basicConfig(level=logging.INFO)

# Token ko direct code me rakhne ke bajaye Environment Variable se uthayein
# Render ke 'Environment' tab me TOKEN naam se key banakar value dalein.
TOKEN = os.environ.get("TOKEN", "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU")

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# --- 3. ADMIN CHECK ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_stat = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return user_stat.status in ["administrator", "creator"]
    except: 
        return False

# --- 4. COMMAND HANDLERS ---

# /show Command
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): 
        return

    # Check if number is provided (e.g., /show 2)
    if not context.args:
        await update.message.reply_text("❗ Galti: Command ke saath number likhein (Ex: /show 2)")
        return

    user_num = context.args[0]
    # Strictly 3 cards limit
    selected_cards = random.sample(DECK, 3)
    
    for card in selected_cards:
        await update.message.reply_text(f"{user_num} cards: {card}")
        await asyncio.sleep(0.05) # Chota delay order ke liye

# /roll Command
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        res = random.randint(1, 6)
        await update.message.reply_text(str(res))

# /sps Command
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        res = random.choice(["Stone", "Paper", "Scissors"])
        await update.message.reply_text(res)

# --- 5. MAIN ---
if __name__ == '__main__':
    # Pehle Flask web server start hoga background thread me
    keep_alive()
    
    # Telegram Bot setup
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    
    print("🚀 Bot Started: Multiple clicks allowed | Strict 3-card limit")
    
    # Bot polling start
    application.run_polling(drop_pending_updates=True)
