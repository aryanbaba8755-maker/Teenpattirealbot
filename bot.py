import random
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU" 
SPECIAL_ID = 1869599187    

# Global Tracker for Steps
# Format: {chat_id: current_step_index}
user_steps = {}

# Sequence Define: O = Odd, E = Even
# 2 Odd, 3 Even, 1 Even, 2 Odd, 3 Even
# Total 11 rolls ki cycle hai
CYCLE = ["O", "O", "E", "E", "E", "E", "O", "O", "E", "E", "E"]

# Cards Setup
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

# --- COMMANDS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_num = context.args[0] if context.args else "1"
    res_cards = random.sample(ALL_CARDS, 3)
    for card in res_cards:
        await update.message.reply_text(f"{user_num} cards {card}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if user_id == SPECIAL_ID:
        # Step track karein
        if chat_id not in user_steps:
            user_steps[chat_id] = 0
            
        current_step = user_steps[chat_id]
        target_type = CYCLE[current_step] # Is step par Odd chahiye ya Even
        
        if target_type == "O":
            num = random.choice([1, 3, 5])
        else:
            num = random.choice([2, 4, 6])
            
        # Agle step par move karein, cycle khatam hone par 0 se restart
        user_steps[chat_id] = (current_step + 1) % len(CYCLE)
    else:
        # Normal users ke liye pure random
        num = random.randint(1, 6)

    await update.message.reply_text(str(num))

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Custom Cycle Active"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    print("Bot is running...")
    application.run_polling(drop_pending_updates=True)
    
