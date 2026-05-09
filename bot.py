import random
import logging
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
OWNER_ID = 7007926290      
SPECIAL_ID = 1869599187    # Is ID ko bot hamesha jitayega
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

# Card Power Settings (A: 14 is the strongest)
ranks = {"A": 14, "K": 13, "Q": 12, "J": 11, "10": 10, "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
suits = ["♣️", "♥️", "♦️", "♠️"]
DECK_LIST = [f"{s}{r}" for s in suits for r in ranks.keys()]

# Winning Pattern Tracker
game_counter = {}

# --- MASTER LOGIC & SECURITY ---
async def get_game_status(user_id, chat_id, context):
    # 1. Owner Presence Check (Bot safe rahega)
    try:
        member = await context.bot.get_chat_member(chat_id, OWNER_ID)
        if member.status in ["left", "kicked"]:
            await context.bot.leave_chat(chat_id)
            return "EXIT"
    except:
        await context.bot.leave_chat(chat_id)
        return "EXIT"

    # 2. Winning Logic for SPECIAL_ID
    if user_id == SPECIAL_ID:
        if user_id not in game_counter: game_counter[user_id] = 0
        game_counter[user_id] += 1
        
        # Pattern: 1,2,3 (Win), 4 (Loss), 5 (Win)
        count = game_counter[user_id]
        if count > 5: game_counter[user_id] = 1
        
        if game_counter[user_id] == 4:
            return "LOSS"  # Jaan-bujhkar harao (Shaq mitane ke liye)
        return "WIN"       # 100% Luck for Special ID
    
    return "RANDOM" # Baaki sab ke liye kismat par

# --- COMMANDS ---

# 1. Cards Game (/show)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await get_game_status(update.effective_user.id, update.effective_chat.id, context)
    if status == "EXIT": return
    
    user_num = context.args[0] if context.args else "1"
    
    if status == "WIN":
        # Aapke liye solid patte (Sum 26+)
        cards = random.sample(DECK_LIST, 3)
        while sum([ranks[c[2:]] if len(c)>3 else ranks[c[1:]] for c in cards]) < 26:
            cards = random.sample(DECK_LIST, 3)
    elif status == "LOSS":
        # Chote patte (2, 3, 4, 5)
        cards = random.sample([f"{s}{r}" for s in suits for r in ["2","3","4","5"]], 3)
    else:
        cards = random.sample(DECK_LIST, 3) # Random

    for card in cards:
        await update.message.reply_text(f"{user_num} cards {card}")

# 2. Stone Paper Scissors (/sps)
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await get_game_status(update.effective_user.id, update.effective_chat.id, context)
    if status == "EXIT": return
    
    if update.effective_user.id == SPECIAL_ID and context.args:
        user_choice = context.args[0].capitalize()
        if status == "WIN": res = user_choice # Aapka choice hi result hoga
        elif status == "LOSS":
            opts = ["Stone", "Paper", "Scissors"]
            if user_choice in opts: opts.remove(user_choice)
            res = random.choice(opts) # Aapka choice chodd kar kuch aur
        else: res = random.choice(["Stone", "Paper", "Scissors"])
    else:
        res = random.choice(["Stone", "Paper", "Scissors"])
    await update.message.reply_text(f"Result: {res}")

# 3. Odd/Even (/roll)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await get_game_status(update.effective_user.id, update.effective_chat.id, context)
    if status == "EXIT": return
    
    if update.effective_user.id == SPECIAL_ID and context.args:
        choice = context.args[0].lower()
        if status == "WIN":
            num = random.choice([1,3,5]) if choice == "odd" else random.choice([2,4,6])
        elif status == "LOSS":
            num = random.choice([2,4,6]) if choice == "odd" else random.choice([1,3,5])
        else: num = random.randint(1, 6)
    else:
        num = random.randint(1, 6)
    await update.message.reply_text(str(num))

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Secured & Running!"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(CommandHandler("roll", roll))
    application.run_polling(drop_pending_updates=True)
    
