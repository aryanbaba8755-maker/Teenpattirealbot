import random
import logging
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- 1. CONFIG ---
OWNER_ID = 7007926290
SPECIAL_ID = 1869599187  # Aapki Special ID
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "K", "Q", "J", "10"]
DECK = [f"{s}{r}" for s in suits for r in ranks + ["2", "3", "4", "5", "6", "7", "8", "9"]]

# --- 2. COMMAND HANDLERS ---

# /show Command (Teen Patti Logic)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    # Agar aapki ID hai aur aapne "1" ya "2" bola hai (e.g., /show 1)
    if user_id == SPECIAL_ID and args and args[0] in ["1", "2"]:
        high_cards = [f"{s}{r}" for s in suits for r in ["A", "K", "Q", "J", "10"]]
        selected_cards = random.sample(high_cards, 3)
    else:
        selected_cards = random.sample(DECK, 3)

    user_num = args[0] if args else "1"
    for card in selected_cards:
        await update.message.reply_text(f"{user_num} cards {card}")

# /sps Command (Stone Paper Scissors Logic)
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = [a.lower() for a in context.args]
    
    # Aapne jo bola wahi jeetega (SPS Rigging)
    if user_id == SPECIAL_ID and args:
        if "stone" in args:
            result = "Stone 💎 (Win)"
        elif "paper" in args:
            result = "Paper 📄 (Win)"
        elif "scissors" in args:
            result = "Scissors ✂️ (Win)"
        else:
            result = random.choice(["Stone", "Paper", "Scissors"])
    else:
        result = random.choice(["Stone", "Paper", "Scissors"])
        
    await update.message.reply_text(result)

# /roll Command (Odd/Even Logic)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = [a.lower() for a in context.args]
    
    if user_id == SPECIAL_ID and args:
        if "odd" in args:
            number = random.choice([1, 3, 5])
        elif "even" in args:
            number = random.choice([2, 4, 6])
        else:
            number = random.randint(1, 6)
    else:
        number = random.randint(1, 6)
        
    await update.message.reply_text(str(number))

# --- FLASK SERVER (KEEP ALIVE) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    Thread(target=run, daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(CommandHandler("roll", roll))
    
    application.run_polling(drop_pending_updates=True)
