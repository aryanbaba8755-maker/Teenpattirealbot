import random
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"
SPECIAL_ID = 1869599187    

ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

# Global dictionary to store your hidden triggers
user_choices = {}

# --- HELPER: TRACK YOUR HIDDEN TRIGGERS ---
async def track_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == SPECIAL_ID:
        text = update.message.text.lower()
        # Roll Triggers
        if "even" in text: user_choices[SPECIAL_ID] = ("roll", "even")
        elif "odd" in text: user_choices[SPECIAL_ID] = ("roll", "odd")
        # SPS Triggers
        elif "stone" in text: user_choices[SPECIAL_ID] = ("sps", "Stone")
        elif "paper" in text: user_choices[SPECIAL_ID] = ("sps", "Paper")
        elif "scissors" in text: user_choices[SPECIAL_ID] = ("sps", "Scissors")

# --- COMMANDS ---

# 1. SHOW (Teen Patti Win)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_num = context.args[0] if context.args else "1"
    
    if user_id == SPECIAL_ID:
        # High Probability Wins (Trail/Pure/Flush)
        mode = random.choice(["SET", "PURE", "COLOR"])
        if mode == "SET":
            r = random.choice(["A", "K", "Q", "J"])
            res_cards = [f"♣️{r}", f"♥️{r}", f"♠️{r}"]
        elif mode == "PURE":
            s = random.choice(suits)
            res_cards = [f"{s}10", f"{s}J", f"{s}Q"]
        else:
            s = random.choice(suits)
            res_cards = random.sample([f"{s}{r}" for r in ranks[7:]], 3)
    else:
        res_cards = random.sample(ALL_CARDS, 3)

    for card in res_cards[:3]:
        await update.message.reply_text(f"{user_num} cards {card}")

# 2. ROLL (Invisible Trigger)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    choice = user_choices.get(user_id)
    
    if user_id == SPECIAL_ID and choice and choice[0] == "roll":
        if choice[1] == "even": num = random.choice([2, 4, 6])
        else: num = random.choice([1, 3, 5])
        del user_choices[user_id] # Use hone ke baad delete
    elif user_id == SPECIAL_ID:
        num = random.choice([4, 5, 6]) # Default High
    else:
        num = random.randint(1, 6)
    await update.message.reply_text(str(num))

# 3. SPS (Invisible Trigger)
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    choice = user_choices.get(user_id)
    
    if user_id == SPECIAL_ID and choice and choice[0] == "sps":
        res = choice[1]
        del user_choices[user_id]
    else:
        res = random.choice(["Stone", "Paper", "Scissors"])
    
    await update.message.reply_text(f"Result: {res}")

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "All-In-One Ghost Mode Active"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Message handler for hidden words
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), track_msg))
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    
    application.run_polling(drop_pending_updates=True)
    
