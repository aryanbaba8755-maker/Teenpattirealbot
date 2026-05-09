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

# Logic Tracker: O = Odd (1,3,5), E = Even (2,4,6)
# Sequence: 2 Odd (O,O) -> 3 Even (E,E,E) -> 1 Even (E) -> 2 Odd (O,O) -> 3 Even (E,E,E)
CYCLE = ["O", "O", "E", "E", "E", "E", "O", "O", "E", "E", "E"]

user_steps = {}  # Track cycle position
last_msg_time = {} # To prevent double replies

# Cards Setup
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

# --- COMMANDS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_num = context.args[0] if context.args else "1"
    res_cards = random.sample(ALL_CARDS, 3)
    # Ek hi message mein teeno cards bhejna better hai taaki spam na ho
    msg = "\n".join([f"{user_num} cards {card}" for card in res_cards])
    await update.message.reply_text(msg)

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    curr_time = time.time()

    # --- Double Reply Prevention ---
    if chat_id in last_msg_time and (curr_time - last_msg_time[chat_id]) < 0.5:
        return
    last_msg_time[chat_id] = curr_time

    # --- Special ID Logic ---
    if user_id == SPECIAL_ID:
        if chat_id not in user_steps:
            user_steps[chat_id] = 0
            
        step_idx = user_steps[chat_id]
        target = CYCLE[step_idx]
        
        if target == "O":
            num = random.choice([1, 3, 5])
        else:
            num = random.choice([2, 4, 6])
            
        # Update step for next time
        user_steps[chat_id] = (step_idx + 1) % len(CYCLE)
    else:
        # Others get pure random
        num = random.randint(1, 6)

    await update.message.reply_text(str(num))

# --- FLASK SERVER (For 24/7 Hosting) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online and Cycle is Active"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- MAIN START ---
if __name__ == '__main__':
    # Start Flask thread
    t = Thread(target=run)
    t.daemon = True
    t.start()

    # Build Telegram Bot
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    
    print("Bot Running...")
    # drop_pending_updates=True purane dabe hue messages ko ignore karta hai
    application.run_polling(drop_pending_updates=True)
    
