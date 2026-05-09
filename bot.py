import random
import logging
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler

# --- 1. FLASK SERVER (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Live 24/7!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- 2. CONFIG & DECK ---
logging.basicConfig(level=logging.INFO)
OWNER_ID = 7007926290
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# Strict Lock: Ek baar mein ek hi command chalne ke liye
processing_chats = set()

# --- 3. HELPERS ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_stat = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return user_stat.status in ["administrator", "creator"]
    except: return False

# Admin (Owner) left group toh Bot bhi left karega
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result and result.from_user.id == OWNER_ID:
        if result.new_chat_member.status in ["left", "kicked"]:
            try:
                await context.bot.leave_chat(result.chat.id)
            except: pass

# --- 4. COMMAND HANDLERS ---

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Anti-Extra Trigger: Agar busy hai toh ignore karega
    if chat_id in processing_chats: return
    
    if await is_admin(update, context):
        if not context.args: return
        
        try:
            processing_chats.add(chat_id)
            user_num = context.args[0]
            selected_cards = random.sample(DECK, 3)
            
            for card in selected_cards:
                # Reply to the command message directly
                await update.message.reply_text(f"{user_num} cards {card}")
                time.sleep(0.08) # Chhota gap stability ke liye
        finally:
            time.sleep(0.3)
            processing_chats.discard(chat_id)

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in processing_chats: return
    
    if await is_admin(update, context):
        try:
            processing_chats.add(chat_id)
            res = random.choice(["Stone", "Paper", "Scissors"])
            await update.message.reply_text(res)
        finally:
            processing_chats.discard(chat_id)

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in processing_chats: return
    
    if await is_admin(update, context):
        try:
            processing_chats.add(chat_id)
            res = random.randint(1, 6)
            await update.message.reply_text(str(res))
        finally:
            processing_chats.discard(chat_id)

# --- 5. MAIN ---
if __name__ == '__main__':
    Thread(target=run, daemon=True).start()
    
    # concurrent_updates=False sabse zaroori hai extra results rokne ke liye
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(False).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(CommandHandler("roll", roll))
    
    # Admin ke leave karne par bot ke leave karne ka system
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))
    
    print("🚀 Bot Started: No Miss, No Extra Mode Active.")
    application.run_polling(drop_pending_updates=True)
    
