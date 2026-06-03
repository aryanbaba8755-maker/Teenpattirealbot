import random
import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- 1. FLASK (KEEP ALIVE) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- 2. CONFIG & DECK ---
TOKEN = os.environ.get("TOKEN", "8699525997:AAGIuGZj2uebowjJKect_xAx2j2QoPTwtMM")
OWNER_ID = 7007926290

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# --- 3. COMMANDS ---
async def is_admin(update, context):
    return update.effective_user.id == OWNER_ID

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        if not context.args:
            await update.message.reply_text("❗ Use: /show [number]")
            return
        
        user_num = context.args[0]
        cards = random.sample(DECK, 3)
        for card in cards:
            await update.message.reply_text(f"{user_num} cards: {card}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        await update.message.reply_text(str(random.choice([1, 3, 5])))

# --- 4. MAIN ---
if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    
    app_bot = ApplicationBuilder().token(TOKEN).build()
    
    app_bot.add_handler(CommandHandler("show", show))
    app_bot.add_handler(CommandHandler("roll", roll))
    
    print("🚀 Bot is running with Cards & Roll!")
    app_bot.run_polling()
