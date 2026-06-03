import random
import logging
import os
import asyncio
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler

# --- 1. FLASK (KEEP ALIVE) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- 2. BOT LOGIC ---
TOKEN = "8699525997:AAGIuGZj2uebowjJKect_xAx2j2QoPTwtMM"
OWNER_ID = 7007926290

async def show(update, context):
    if update.effective_user.id == OWNER_ID:
        if context.args:
            user_num = context.args[0]
            suits = ["♣️", "♥️", "♦️", "♠️"]
            ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
            for _ in range(3):
                card = f"{random.choice(suits)}{random.choice(ranks)}"
                await update.message.reply_text(f"{user_num} cards: {card}")
                await asyncio.sleep(0.1)

async def roll(update, context):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text(str(random.choice([1,2,3,4,5,6])))

# --- 3. FIX FOR EVENT LOOP ERROR ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("show", show))
    app_bot.add_handler(CommandHandler("roll", roll))
    
    print("🚀 Bot is running perfectly!")
    await app_bot.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
