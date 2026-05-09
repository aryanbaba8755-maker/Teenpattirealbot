import random
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"
SPECIAL_ID = 1869599187    

ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

# --- WINNING LOGIC ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Admin ho ya nahi, ye check user_id se hoga
    user_id = update.effective_user.id
    user_num = context.args[0] if context.args else "1"
    
    try:
        if int(user_num) > 100: return
    except: user_num = "1"

    # --- TEEN PATTI RIGGED WINNING ---
    if user_id == SPECIAL_ID:
        # Aap admin ho isliye bot aapko pehle priority dega
        # Trail (Set) - Isse bada kuch nahi hota game mein
        r = random.choice(["A", "K", "Q", "J"])
        res_cards = [f"♣️{r}", f"♥️{r}", f"♠️{r}"]
    else:
        # Opponent ke liye hamesha chote patte (2 to 7 ke beech)
        res_cards = [f"{random.choice(suits)}{random.choice(ranks[:5])}", 
                     f"{random.choice(suits)}{random.choice(ranks[:4])}", 
                     f"{random.choice(suits)}{random.choice(ranks[:6])}"]

    # STRICTLY 3 CARDS ONLY
    random.shuffle(res_cards)
    for card in res_cards[:3]:
        await update.message.reply_text(f"{user_num} cards {card}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == SPECIAL_ID:
        num = random.choice([4, 5, 6])
    else:
        num = random.choice([1, 2, 3]) # Opponent hamesha kam score karega
    await update.message.reply_text(str(num))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    res = random.choice(["Stone", "Paper", "Scissors"])
    if user_id == SPECIAL_ID and context.args:
        res = context.args[0].capitalize()
    await update.message.reply_text(f"Result: {res}")

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Admin Win Mode Active"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    
    # application build with direct settings
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers (Admin status doesn't matter here, only ID matters)
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    
    # drop_pending_updates=True is MUST to clear old admin commands
    application.run_polling(drop_pending_updates=True)
