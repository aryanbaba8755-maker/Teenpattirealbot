import random
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"
SPECIAL_ID = 1869599187    

# Full 52 Cards Deck
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

# --- COMMANDS ---

# 1. SHOW (Strictly 3 Cards Only)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Auto-Left Logic (If Special ID leaves)
    try:
        member = await context.bot.get_chat_member(chat_id, SPECIAL_ID)
        if member.status in ["left", "kicked"]:
            await context.bot.leave_chat(chat_id)
            return
    except: return

    # User Number (1-100)
    user_num = context.args[0] if context.args else "1"
    try:
        if int(user_num) > 100: return
    except: user_num = "1"

    # --- TEEN PATTI WIN LOGIC ---
    if user_id == SPECIAL_ID:
        # Hamesha strong sets: Color, Sequence ya High Pair
        mode = random.choice(["FLUSH", "SEQ", "PAIR"])
        if mode == "FLUSH":
            s = random.choice(suits)
            res_cards = random.sample([f"{s}{r}" for r in ranks], 3)
        elif mode == "SEQ":
            start = random.randint(4, 10)
            res_cards = [f"{random.choice(suits)}{ranks[start]}", f"{random.choice(suits)}{ranks[start+1]}", f"{random.choice(suits)}{ranks[start+2]}"]
        else:
            r = random.choice(["A", "K", "Q", "J"])
            res_cards = [f"♣️{r}", f"♥️{r}", f"{random.choice(suits)}{random.choice(ranks[:5])}"]
    else:
        res_cards = random.sample(ALL_CARDS, 3)

    # Ek hi message mein teeno patte ya alag-alag, par sirf 3!
    for card in res_cards[:3]:
        await update.message.reply_text(f"{user_num} cards {card}")

# 2. ROLL (Single Result Only)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    arg = context.args[0].lower() if context.args else ""
    
    # Logic to fix multiple rolls
    num = random.randint(1, 6)
    if user_id == SPECIAL_ID:
        if "even" in arg: num = random.choice([2, 4, 6])
        elif "odd" in arg: num = random.choice([1, 3, 5])
        else: num = random.choice([4, 5, 6]) # Lucky high numbers
        
    await update.message.reply_text(str(num))

# 3. SPS (Single Result)
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    res = random.choice(["Stone", "Paper", "Scissors"])
    if user_id == SPECIAL_ID and context.args:
        res = context.args[0].capitalize()
    await update.message.reply_text(f"Result: {res}")

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Active"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    
    # drop_pending_updates=True is MUST to stop duplicate messages
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    
    print("Bot is starting...")
    application.run_polling(drop_pending_updates=True)
    
