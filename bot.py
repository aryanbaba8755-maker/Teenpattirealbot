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

# Cards Deck
ranks = {"A": 14, "K": 13, "Q": 12, "J": 11, "10": 10, "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
suits = ["♣️", "♥️", "♦️", "♠️"]
DECK = [f"{s}{r}" for s in suits for r in ranks.keys()]

# --- SECURITY ---
async def check_bot_safety(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, OWNER_ID)
        if member.status in ["left", "kicked"]:
            await context.bot.leave_chat(update.effective_chat.id)
            return False
        return True
    except:
        await context.bot.leave_chat(update.effective_chat.id)
        return False

# --- COMMANDS ---

# 1. Cards (/show)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_safety(update, context): return
    
    user_id = update.effective_user.id
    user_num = context.args[0] if context.args else "1"

    # Har baar fresh 3 cards pick honge
    cards = random.sample(DECK, 3)

    # Special ID Winning Logic
    if user_id == SPECIAL_ID:
        # Jab tak total value 26 se kam hai, tab tak naye cards pick karo
        while sum([ranks[c[2:]] if len(c)>3 else ranks[c[1:]] for c in cards]) < 26:
            cards = random.sample(DECK, 3)

    # Response
    for card in cards:
        await update.message.reply_text(f"{user_num} cards {card}")

# 2. Roll (/roll) - Pure Random 1 to 6
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_safety(update, context): return
    num = random.randint(1, 6)
    await update.message.reply_text(str(num))

# 3. SPS (/sps)
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_bot_safety(update, context): return
    res = random.choice(["Stone", "Paper", "Scissors"])
    if update.effective_user.id == SPECIAL_ID and context.args:
        res = context.args[0].capitalize()
    await update.message.reply_text(f"Result: {res}")

# --- WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    application.run_polling(drop_pending_updates=True)
    
