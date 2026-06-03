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

Thread(target=run, daemon=True).start()

# --- 2. CONFIG ---
logging.basicConfig(level=logging.INFO)
TOKEN = "8699525997:AAGIuGZj2uebowjJKect_xAx2j2QoPTwtMM"

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# Lock dictionary taaki ek time par ek hi request chale
processing_locks = {}

# --- 3. COMMAND HANDLERS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if processing_locks.get(chat_id): return # Ignore agar pehle se chal raha hai
    
    if not context.args:
        await update.message.reply_text("❗ Use: /show 1")
        return

    processing_locks[chat_id] = True
    user_num = context.args[0]
    user_name = update.effective_user.first_name or "ARJUNBHAI"
    selected_cards = random.sample(DECK, 3)
    
    for card in selected_cards:
        await update.message.reply_text(f"{user_name}\n/show {user_num}\n{user_num} cards: {card}", quote=True)
        await asyncio.sleep(0.3)
    
    processing_locks[chat_id] = False

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if processing_locks.get(chat_id): return
    
    processing_locks[chat_id] = True
    res = random.randint(1, 6)
    await update.message.reply_text(str(res), quote=True)
    await asyncio.sleep(0.5)
    processing_locks[chat_id] = False

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if processing_locks.get(chat_id): return
    
    processing_locks[chat_id] = True
    res = random.choice(["Stone", "Paper", "Scissors"])
    await update.message.reply_text(res, quote=True)
    await asyncio.sleep(0.5)
    processing_locks[chat_id] = False

# --- 4. MAIN ---
if __name__ == '__main__':
    # concurrent_updates=False karke sabhi requests ko queue mein daal diya hai
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(False).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    
    print("🚀 Bot Started with Anti-Spam Lock!")
    application.run_polling(drop_pending_updates=True)
