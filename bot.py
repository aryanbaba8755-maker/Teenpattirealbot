import random
import logging
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
OWNER_ID = 7007926290      
SPECIAL_ID = 1869599187    
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

# Card Power Settings
ranks = {"A": 14, "K": 13, "Q": 12, "J": 11, "10": 10, "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
suits = ["♣️", "♥️", "♦️", "♠️"]
DECK_LIST = [f"{s}{r}" for s in suits for r in ranks.keys()]
game_counter = {}

# --- MASTER LOGIC ---
async def get_game_status(user_id, chat_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id, OWNER_ID)
        if member.status in ["left", "kicked"]:
            await context.bot.leave_chat(chat_id)
            return "EXIT"
    except:
        await context.bot.leave_chat(chat_id)
        return "EXIT"

    if user_id == SPECIAL_ID:
        if user_id not in game_counter: game_counter[user_id] = 0
        game_counter[user_id] += 1
        if game_counter[user_id] > 5: game_counter[user_id] = 1
        
        # Game 4 is a small win/loss to avoid suspicion
        if game_counter[user_id] == 4: return "LOSS"
        return "WIN"
    return "RANDOM"

# --- COMMANDS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await get_game_status(update.effective_user.id, update.effective_chat.id, context)
    if status == "EXIT": return
    user_num = context.args[0] if context.args else "1"
    
    if status == "WIN":
        cards = random.sample(DECK_LIST, 3)
        while sum([ranks[c[2:]] if len(c)>3 else ranks[c[1:]] for c in cards]) < 26:
            cards = random.sample(DECK_LIST, 3)
    elif status == "LOSS":
        # Low cards for loss round
        cards = random.sample([f"{s}{r}" for s in suits for r in ["2","3","4","5"]], 3)
    else:
        cards = random.sample(DECK_LIST, 3)
        
    for card in cards: 
        await update.message.reply_text(f"{user_num} cards {card}")

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await get_game_status(update.effective_user.id, update.effective_chat.id, context)
    if status == "EXIT": return
    
    if update.effective_user.id == SPECIAL_ID and context.args:
        choice = context.args[0].capitalize()
        if status == "WIN": res = choice
        else:
            opts = ["Stone", "Paper", "Scissors"]
            if choice in opts: opts.remove(choice)
            res = random.choice(opts)
    else:
        res = random.choice(["Stone", "Paper", "Scissors"])
    await update.message.reply_text(f"Result: {res}")

# --- FIXED ROLL (ONLY 2, 4, 6) ---
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await get_game_status(update.effective_user.id, update.effective_chat.id, context)
    if status == "EXIT": return
    
    # Is poore function mein sirf [2, 4, 6] hi option hai
    even_only = [2, 4, 6]
    
    if update.effective_user.id == SPECIAL_ID:
        if status == "WIN":
            num = random.choice(even_only) # 2, 4, or 6
        else:
            num = 2 # Forced 2 (Small even) for the loss round
    else:
        # Others also get only even so no one suspects the bot
        num = random.choice(even_only)
        
    await update.message.reply_text(str(num))

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Even Only Mode Active"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(CommandHandler("roll", roll))
    application.run_polling(drop_pending_updates=True)
