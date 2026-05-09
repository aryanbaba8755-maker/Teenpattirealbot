import random
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"
SPECIAL_ID = 1869599187    
OWNER_ID = 7007926290      

# Full 52 Cards Deck
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

# --- COMMANDS ---

# 1. SHOW COMMAND (Strictly 3 Cards Only)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Auto-Left Logic (Safety Check)
    try:
        member = await context.bot.get_chat_member(chat_id, SPECIAL_ID)
        if member.status in ["left", "kicked"]:
            await context.bot.leave_chat(chat_id)
            return
    except:
        await context.bot.leave_chat(chat_id)
        return

    # Argument Handling (1-100)
    user_num = "1"
    if context.args:
        try:
            val = int(context.args[0])
            if 1 <= val <= 100: user_num = str(val)
            else: return # Ignore if > 100
        except: user_num = "1"

    # --- WINNING LOGIC (TEEN PATTI STYLE) ---
    if user_id == SPECIAL_ID:
        # Special ID gets High Combinations
        win_modes = ["TRAIL", "SEQUENCE", "FLUSH", "PAIR_A"]
        mode = random.choice(win_modes)

        if mode == "TRAIL": # A-A-A, K-K-K, etc.
            r = random.choice(["A", "K", "Q", "J", "10"])
            res_cards = random.sample([f"{s}{r}" for s in suits], 3)
        elif mode == "SEQUENCE": # J-Q-K, 10-J-Q
            start = random.randint(5, 10)
            res_cards = [f"{random.choice(suits)}{ranks[start]}", 
                         f"{random.choice(suits)}{ranks[start+1]}", 
                         f"{random.choice(suits)}{ranks[start+2]}"]
        elif mode == "FLUSH": # Same Suit
            s = random.choice(suits)
            res_cards = random.sample([f"{s}{r}" for r in ranks], 3)
        else: # Strong Pair
            r = "A"
            other = random.choice(ranks[:-1])
            res_cards = [f"♣️{r}", f"♥️{r}", f"{random.choice(suits)}{other}"]
    else:
        # Others get pure random (Mostly low High Cards)
        res_cards = random.sample(ALL_CARDS, 3)

    # Output: Exactly 3 messages for 3 cards
    random.shuffle(res_cards)
    for card in res_cards[:3]: # Forcefully only 3 cards
        await update.message.reply_text(f"{user_num} cards {card}")

# 2. ROLL COMMAND (100% Logic)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    num = random.randint(1, 6)
    if user_id == SPECIAL_ID and context.args:
        arg = context.args[0].lower()
        if "even" in arg: num = random.choice([2, 4, 6])
        elif "odd" in arg: num = random.choice([1, 3, 5])
    await update.message.reply_text(str(num))

# 3. SPS COMMAND (100% Logic)
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    res = random.choice(["Stone", "Paper", "Scissors"])
    if user_id == SPECIAL_ID and context.args:
        res = context.args[0].capitalize()
    await update.message.reply_text(f"Result: {res}")

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot Active: 3-Card Strict Mode"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    application.run_polling(drop_pending_updates=True)
    
