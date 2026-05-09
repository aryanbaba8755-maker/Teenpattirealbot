import random
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "YAHAN_NAYA_TOKEN_DALO" # Naya token zaroori hai
SPECIAL_ID = 1869599187    

ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_num = context.args[0] if context.args else "1"

    # --- 100% WINNING LOGIC FOR PARTH ---
    if user_id == SPECIAL_ID:
        # Aapko hamesha Trail (AAA, KKK, QQQ) milega
        r = random.choice(["A", "K", "Q", "J"])
        res_cards = [f"♣️{r}", f"♥️{r}", f"♠️{r}"]
    else:
        # Opponents ko hamesha chote aur bekar patte milenge
        res_cards = [f"{random.choice(suits)}{random.choice(ranks[:4])}", 
                     f"{random.choice(suits)}{random.choice(ranks[:3])}", 
                     f"{random.choice(suits)}{random.choice(ranks[:5])}"]

    # STRICTLY 3 MESSAGES ONLY
    for card in res_cards[:3]:
        await update.message.reply_text(f"{user_num} cards {card}")

# --- ROLL & SPS (WIN LOGIC) ---
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == SPECIAL_ID:
        await update.message.reply_text(str(random.choice([4, 5, 6])))
    else:
        await update.message.reply_text(str(random.choice([1, 2, 3])))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = random.choice(["Stone", "Paper", "Scissors"])
    if update.effective_user.id == SPECIAL_ID and context.args:
        res = context.args[0].capitalize()
    await update.message.reply_text(f"Result: {res}")

# SERVER & POLLING
app = Flask('')
@app.route('/')
def home(): return "Ready to Win"

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    application.run_polling(drop_pending_updates=True)
    
