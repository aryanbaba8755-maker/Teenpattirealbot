import random
import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"
SPECIAL_ID = 1869599187    
OWNER_ID = 7007926290      

# Cards Deck
ranks = {"A": 14, "K": 13, "Q": 12, "J": 11, "10": 10, "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks.keys()]

# --- COMMANDS ---

# 1. SHOW COMMAND (Ab har haal mein chalega)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Check if Special ID is in group, else leave
    try:
        member = await context.bot.get_chat_member(chat_id, SPECIAL_ID)
        if member.status in ["left", "kicked"]:
            await context.bot.leave_chat(chat_id)
            return
    except:
        await context.bot.leave_chat(chat_id)
        return

    # User Number Handling
    user_num = "1" # Default
    if context.args:
        try:
            val = int(context.args[0])
            if 1 <= val <= 100:
                user_num = str(val)
            else:
                return # 100 se bada number toh ignore
        except ValueError:
            user_num = "1"

    # Winning Logic
    if user_id == SPECIAL_ID:
        # 100% Jeetne wale bade patte
        high_pool = [f"{s}{r}" for s in suits for r in ["A", "K", "Q", "J", "10"]]
        res_cards = random.sample(high_pool, 3)
    else:
        res_cards = random.sample(ALL_CARDS, 3)

    for card in res_cards:
        await update.message.reply_text(f"{user_num} cards {card}")

# 2. ROLL COMMAND
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    arg = context.args[0].lower() if context.args else ""
    
    if user_id == SPECIAL_ID:
        if "odd" in arg: num = random.choice([1, 3, 5])
        elif "even" in arg: num = random.choice([2, 4, 6])
        else: num = random.choice([4, 5, 6])
    else:
        num = random.randint(1, 6)
    await update.message.reply_text(str(num))

# 3. SPS COMMAND
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == SPECIAL_ID and context.args:
        result = context.args[0].capitalize()
    else:
        result = random.choice(["Stone", "Paper", "Scissors"])
    await update.message.reply_text(f"Result: {result}")

# --- WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    Thread(target=run).start()
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    
    application.run_polling(drop_pending_updates=True)
    
