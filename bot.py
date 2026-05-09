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

# Global variable to store your last message preference
last_pref = {}

# --- HELPER: SAVE YOUR PREFERENCE ---
async def track_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == SPECIAL_ID:
        text = update.message.text.lower()
        if "even" in text: last_pref[SPECIAL_ID] = "even"
        elif "odd" in text: last_pref[SPECIAL_ID] = "odd"

# --- COMMANDS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_num = context.args[0] if context.args else "1"
    
    if user_id == SPECIAL_ID:
        # Jeetne wale combinations: Mix rakha hai taaki shaq na ho
        mode = random.choice(["SET", "PURE", "COLOR", "HIGH_A"])
        if mode == "SET":
            r = random.choice(["A", "K", "Q", "J", "10"])
            res_cards = [f"♣️{r}", f"♥️{r}", f"♠️{r}"]
        elif mode == "PURE":
            s = random.choice(suits)
            res_cards = [f"{s}10", f"{s}J", f"{s}Q"]
        else: # Color ya High Ace
            s = random.choice(suits)
            res_cards = [f"{s}A", f"{s}{random.choice(ranks[5:10])}", f"{s}{random.choice(ranks[:5])}"]
    else:
        res_cards = random.sample(ALL_CARDS, 3)

    for card in res_cards[:3]:
        await update.message.reply_text(f"{user_num} cards {card}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pref = last_pref.get(user_id, "high") # Default high numbers
    
    if user_id == SPECIAL_ID:
        if pref == "even": num = random.choice([2, 4, 6])
        elif pref == "odd": num = random.choice([1, 3, 5])
        else: num = random.choice([4, 5, 6])
    else:
        num = random.randint(1, 6)
        
    await update.message.reply_text(str(num))
    # Reset preference after roll
    if user_id in last_pref: del last_pref[user_id]

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Ghost Mode Active"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Ye handler aapke normal messages ko read karega
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), track_msg))
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    
    application.run_polling(drop_pending_updates=True)
    
