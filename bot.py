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
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. CONFIG ---
logging.basicConfig(level=logging.INFO)

OWNER_ID = 7007926290
TOKEN = os.environ.get("TOKEN", "8699525997:AAGIuGZj2uebowjJKect_xAx2j2QoPTwtMM")

# DECK Setup
suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# --- 3. ADMIN CHECK ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        return True
    try:
        user_stat = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return user_stat.status in ["administrator", "creator"]
    except: 
        return False

# --- 4. COMMAND HANDLERS ---

# /show Command
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return

    if not context.args:
        await update.message.reply_text("❗ Galti: Command ke saath number likhein (Ex: /show 2)")
        return

    user_num = context.args[0]
    selected_cards = random.sample(DECK, 3)
    
    for card in selected_cards:
        await update.message.reply_for_text(f"{user_num} cards: {card}")
        await asyncio.sleep(0.05)

# /roll Command (Sirf 1, 3, 5)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        res = random.choice([1, 3, 5])
        await update.message.reply_text(str(res))

# /sps Command
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        res = random.choice(["Stone", "Paper", "Scissors"])
        await update.message.reply_text(res)

# --- 5. MAIN ---
if __name__ == '__main__':
    keep_alive()
    
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    
    print("🚀 Bot Started Successfully!")
    application.run_polling(drop_pending_updates=True)
    
