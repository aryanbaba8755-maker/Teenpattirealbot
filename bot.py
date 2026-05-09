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

# Strict Lock: Ek baar mein ek hi command process hogi
processing_chats = set()

# Cards & SPS Setup
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]
SPS_OPTIONS = ["Stone", "Paper", "Scissors"]

# --- FUNCTIONS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # AGAR BOT BUSY HAI TOH BILKUL REPLY NAHI KAREGA
    if chat_id in processing_chats:
        return

    try:
        processing_chats.add(chat_id) # Lock lagao
        user_num = context.args[0] if context.args else "1"
        
        # 100% Guarantee: Sirf 3 cards hi select honge
        res_cards = random.sample(ALL_CARDS, 3)
        
        for card in res_cards:
            text = f"{user_num} cards {card}"
            # Seedha message bina reply header ke
            await context.bot.send_message(chat_id=chat_id, text=text)
            time.sleep(0.05) # Boht chhota gap
            
    finally:
        # Command poori hone ke 0.5s baad hi agle ke liye ready hoga
        time.sleep(0.5)
        processing_chats.discard(chat_id) # Lock hatao

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in processing_chats: return

    try:
        processing_chats.add(chat_id)
        num = random.randint(1, 6)
        await context.bot.send_message(chat_id=chat_id, text=str(num))
    finally:
        time.sleep(0.3)
        processing_chats.discard(chat_id)

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in processing_chats: return

    try:
        processing_chats.add(chat_id)
        choice = random.choice(SPS_OPTIONS)
        await context.bot.send_message(chat_id=chat_id, text=choice)
    finally:
        time.sleep(0.3)
        processing_chats.discard(chat_id)

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result and result.from_user.id == OWNER_ID:
        if result.new_chat_member.status in ["left", "kicked"]:
            try:
                await context.bot.leave_chat(result.chat.id)
            except: pass

# --- SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Ready"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- MAIN ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()

    # concurrent_updates=False karke bot ko force kiya hai ki ek ek karke hi handle kare
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(False) 
        .build()
    )
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))
    
    print("Anti-Extra Mode Active...")
    # drop_pending_updates=True sabse zaroori hai extra messages rokne ke liye
    application.run_polling(drop_pending_updates=True)
