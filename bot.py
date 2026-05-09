import random
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU" 
OWNER_ID = 1869599187 

# Single Command Lock
is_processing = {}

# Cards & SPS Setup
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]
SPS_OPTIONS = ["Stone", "Paper", "Scissors"]

# --- FUNCTIONS ---

# 1. SHOW (Wahi style jo aapne screenshot mein dikhaya)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if is_processing.get(chat_id): return

    try:
        is_processing[chat_id] = True
        user_num = context.args[0] if context.args else "1"
        res_cards = random.sample(ALL_CARDS, 3)
        
        for card in res_cards:
            text = f"{user_num} cards {card}"
            # Seedha message bhejega bina reply kiye
            await context.bot.send_message(chat_id=chat_id, text=text)
            time.sleep(0.1) 
    finally:
        is_processing[chat_id] = False

# 2. ROLL (Sirf Number - No Emoji, No Reply, No Miss)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if is_processing.get(chat_id): return

    try:
        is_processing[chat_id] = True
        num = random.randint(1, 6)
        # Seedha number bhej raha hai bina kisi formatting ke
        await context.bot.send_message(chat_id=chat_id, text=str(num))
    finally:
        is_processing[chat_id] = False

# 3. SPS (Plain Text Only)
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if is_processing.get(chat_id): return

    try:
        is_processing[chat_id] = True
        choice = random.choice(SPS_OPTIONS)
        await context.bot.send_message(chat_id=chat_id, text=choice)
    finally:
        is_processing[chat_id] = False

# 4. Auto-Leave Logic
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result and result.from_user.id == OWNER_ID:
        if result.new_chat_member.status in ["left", "kicked"]:
            try:
                await context.bot.leave_chat(result.chat.id)
            except: pass

# --- FLASK SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Online"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- MAIN ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()

    # Timeouts badha diye hain taaki ek bhi command miss na ho
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(40.0)
        .read_timeout(40.0)
        .concurrent_updates(True)
        .build()
    )
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))
    
    print("Bot 100% Fixed Style mein chalu hai...")
    application.run_polling(drop_pending_updates=True)
