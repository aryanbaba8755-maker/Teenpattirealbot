import random
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

# Global storage for Streak
last_roll_result = {} # Stores {'chat_id': {'value': 2, 'time': 12345}}

# Cards Setup
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

# --- COMMANDS ---

# 1. SHOW (Normal Random - Max 3 Cards)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_num = context.args[0] if context.args else "1"
    
    # Strictly Random for everyone
    res_cards = random.sample(ALL_CARDS, 3)

    # Strictly 3 cards only
    for card in res_cards:
        await update.message.reply_text(f"{user_num} cards {card}")

# 2. ROLL (Streak Logic)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    current_time = time.time()
    
    # Check if there is a streak (last roll within 60 seconds)
    if chat_id in last_roll_result:
        last_data = last_roll_result[chat_id]
        if current_time - last_data['time'] < 60: # 1 minute window
            last_val = last_data['value']
            # Agar pichla Even tha toh is baar bhi Even
            if last_val % 2 == 0:
                num = random.choice([2, 4, 6])
            else:
                num = random.choice([1, 3, 5])
        else:
            num = random.randint(1, 6)
    else:
        num = random.randint(1, 6)

    # Save current result for next "tap"/command
    last_roll_result[chat_id] = {'value': num, 'time': current_time}
    
    await update.message.reply_text(str(num))

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Normal Cards + Roll Streak Active"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    
    # drop_pending_updates=True double message rokne ke liye
    application.run_polling(drop_pending_updates=True)
