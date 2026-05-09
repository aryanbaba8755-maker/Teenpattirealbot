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

ranks = {"A": 14, "K": 13, "Q": 12, "J": 11, "10": 10, "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
suits = ["♣️", "♥️", "♦️", "♠️"]
DECK_LIST = [f"{s}{r}" for s in suits for r in ranks.keys()]

# Game Counter for Pattern: Win(1)-Win(2)-Win(3)-Loss(4)-Win(5)
game_counter = {}

# --- SECURITY & PATTERN HELPER ---
async def check_security_and_pattern(user_id, chat_id, context):
    # 1. Owner Presence Check
    try:
        member = await context.bot.get_chat_member(chat_id, OWNER_ID)
        if member.status in ["left", "kicked"]:
            await context.bot.leave_chat(chat_id)
            return "LEAVE"
    except:
        await context.bot.leave_chat(chat_id)
        return "LEAVE"

    # 2. Pattern Logic for Special ID
    if user_id == SPECIAL_ID:
        if user_id not in game_counter:
            game_counter[user_id] = 0
        
        game_counter[user_id] += 1
        current_game = game_counter[user_id]

        # Reset counter after 5 games
        if current_game > 5:
            game_counter[user_id] = 1
            current_game = 1
        
        # Game 4 is a FORCE LOSS
        if current_game == 4:
            return "FORCE_LOSS"
        # Games 1, 2, 3, 5 are WEIGHTED WINS
        return "WEIGHTED_WIN"
    
    return "RANDOM"

# --- RIGGING HELPERS ---
def get_cards(status):
    if status == "WEIGHTED_WIN":
        selected = random.sample(DECK_LIST, 3)
        while sum([ranks[c[2:]] if len(c)>3 else ranks[c[1:]] for c in selected]) < 25:
            selected = random.sample(DECK_LIST, 3)
        return selected
    elif status == "FORCE_LOSS":
        low_deck = [f"{s}{r}" for s in suits for r in ["2", "3", "4", "5"]]
        return random.sample(low_deck, 3)
    return random.sample(DECK_LIST, 3)

def get_result(user_choice, game_type, status):
    if status == "WEIGHTED_WIN":
        return user_choice.capitalize() # 100% Win in weighted turns
    elif status == "FORCE_LOSS":
        # Return the opposite to ensure loss
        if game_type == "HT":
            return "Tails" if user_choice.lower() in ["h", "heads"] else "Heads"
        else:
            options = ["Stone", "Paper", "Scissors"]
            choice_cap = user_choice.capitalize()
            if choice_cap in options: options.remove(choice_cap)
            return random.choice(options)
    
    # Default Random for others
    if game_type == "HT": return random.choice(["Heads", "Tails"])
    return random.choice(["Stone", "Paper", "Scissors"])

# --- COMMANDS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await check_security_and_pattern(update.effective_user.id, update.effective_chat.id, context)
    if status == "LEAVE": return
    
    user_num = context.args[0] if context.args else "1"
    cards = get_cards(status)
    for card in cards:
        await update.message.reply_text(f"{user_num} cards {card}")

async def toss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await check_security_and_pattern(update.effective_user.id, update.effective_chat.id, context)
    if status == "LEAVE": return
    
    if update.effective_user.id == SPECIAL_ID and context.args:
        user_choice = "heads" if context.args[0].lower() in ["h", "heads"] else "tails"
        res = get_result(user_choice, "HT", status)
    else: res = random.choice(["Heads", "Tails"])
    await update.message.reply_text(f"🪙 Toss Result: {res}")

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await check_security_and_pattern(update.effective_user.id, update.effective_chat.id, context)
    if status == "LEAVE": return
    
    if update.effective_user.id == SPECIAL_ID and context.args:
        user_choice = context.args[0].lower()
        res = get_result(user_choice, "SPS", status)
    else: res = random.choice(["Stone", "Paper", "Scissors"])
    await update.message.reply_text(f"Result: {res}")

# --- WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Live with Pattern Logic!"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("toss", toss))
    application.add_handler(CommandHandler("sps", sps))
    application.run_polling(drop_pending_updates=True)
    
