import random
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"
SPECIAL_ID = 1869599187    

# Cards Deck (Pure 52 Cards)
ranks = {"A": 14, "K": 13, "Q": 12, "J": 11, "10": 10, "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks.keys()]

# Card Value Calculator
def get_total(cards_list):
    total = 0
    for c in cards_list:
        # Suit ka symbol hata kar rank nikalna
        r = c[1:] if len(c) == 2 or len(c) == 3 else c[2:]
        total += ranks.get(r, 0)
    return total

# --- COMMANDS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Auto-Left Logic
    try:
        member = await context.bot.get_chat_member(chat_id, SPECIAL_ID)
        if member.status in ["left", "kicked"]:
            await context.bot.leave_chat(chat_id)
            return
    except:
        await context.bot.leave_chat(chat_id)
        return

    # User Number Handling (Limit 1-100)
    user_num = "1"
    if context.args:
        try:
            val = int(context.args[0])
            if 1 <= val <= 100: user_num = str(val)
            else: return
        except: user_num = "1"

    # --- SMART WINNING LOGIC ---
    if user_id == SPECIAL_ID:
        # 1. Pehle ek dummy opponent ka score socho (Random 15 se 25 ke beech)
        opponent_score = random.randint(15, 25)
        
        # 2. Aapke liye patte nikalo jo opponent se zyada hon
        attempts = 0
        while attempts < 100:
            res_cards = random.sample(ALL_CARDS, 3)
            my_score = get_total(res_cards)
            # Condition: Aapka score opponent se zyada ho par bahut zyada nahi (Natural dikhne ke liye)
            if my_score > opponent_score:
                break
            attempts += 1
    else:
        # Baaki sab ke liye pure random (Kuch bhi aa sakta hai)
        res_cards = random.sample(ALL_CARDS, 3)

    # Output
    for card in res_cards:
        await update.message.reply_text(f"{user_num} cards {card}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    num = random.randint(1, 6) # Sabke liye random 1-6
    
    if user_id == SPECIAL_ID and context.args:
        arg = context.args[0].lower()
        if "even" in arg: num = random.choice([2, 4, 6])
        elif "odd" in arg: num = random.choice([1, 3, 5])
    
    await update.message.reply_text(str(num))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    res = random.choice(["Stone", "Paper", "Scissors"])
    if user_id == SPECIAL_ID and context.args:
        res = context.args[0].capitalize()
    await update.message.reply_text(f"Result: {res}")

# --- WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Smart Win Active"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    Thread(target=run).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    application.run_polling(drop_pending_updates=True)
    
