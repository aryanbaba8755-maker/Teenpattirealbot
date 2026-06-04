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
TOKEN = "8699525997:AAGBZ1WbzgnY2BXHzdk2vhNf3dGi_khiLBE"

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# --- 3. ADMIN CHECK ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_stat = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return user_stat.status in ["administrator", "creator"]
    except: return False

# --- 4. COMMAND HANDLERS ---

# /show Command
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not await is_admin(update, context): return

    # Check if number is provided (e.g., /show 2)
    if not context.args:
        await update.message.reply_text("❗ Galti: Command ke saath number likhein (Ex: /show 2)")
        return

    user_num = context.args[0]
    # Strictly 3 cards limit
    selected_cards = random.sample(DECK, 3)
    
    for card in selected_cards:
        # Simple format without 🃏 emoji
        await update.message.reply_text(f"{user_num} cards: {card}")
        await asyncio.sleep(0.05) # Chota delay for order

# /roll Command
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        res = random.randint(1, 6)
        # Direct number reply
        await update.message.reply_text(str(res))

# /sps Command
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        res = random.choice(["Stone", "Paper", "Scissors"])
        await update.message.reply_text(res)

# --- 5. MAIN ---
if __name__ == '__main__':
    
    keep_alive()
    
    # concurrent_updates=True handles multiple clicks/double clicks
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    
    print("🚀 Bot Started: Multiple clicks allowed | Strict 3-card limit")
    application.run_polling(drop_pending_updates=True)
