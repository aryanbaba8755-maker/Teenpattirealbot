import random
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU" 
SPECIAL_ID = 1869599187    

# Global Counter to track rolls
roll_count = {} # {'chat_id': count}

# Cards Setup
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

# --- COMMANDS ---

# 1. SHOW (Strictly 3 Cards Only - Random)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_num = context.args[0] if context.args else "1"
    res_cards = random.sample(ALL_CARDS, 3)
    for card in res_cards:
        await update.message.reply_text(f"{user_num} cards {card}")

# 2. ROLL (10 ODD -> 3 EVEN Pattern)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Initialize count for this chat if not exists
    if chat_id not in roll_count:
        roll_count[chat_id] = 0
    
    # Logic for Special ID (Parth)
    if user_id == SPECIAL_ID:
        count = roll_count[chat_id]
        
        if count < 10:
            # First 10 times: ODD
            num = random.choice([1, 3, 5])
        elif count < 13:
            # Next 3 times: EVEN
            num = random.choice([2, 4, 6])
        else:
            # Reset after 13 rolls
            roll_count[chat_id] = 0
            num = random.choice([1, 3, 5])
        
        roll_count[chat_id] += 1
    else:
        # Others get pure random
        num = random.randint(1, 6)

    await update.message.reply_text(str(num))

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "10-3 Cycle Active"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.run_polling(drop_pending_updates=True)
    
