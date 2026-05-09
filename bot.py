import random
import os
import time
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler

# --- 1. FLASK SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Active!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- 2. CONFIG ---
logging.basicConfig(level=logging.INFO)
OWNER_ID = 7007926290
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

# Winning Pattern
WIN_PATTERN = (['O']*3 + ['E']*2 + ['O']*1 + ['E']*4 + ['O']*2 + ['E']*2 + ['O']*1 + ['E']*3 + ['O']*2)
roll_counts = {}

def get_pattern_roll(chat_id):
    if chat_id not in roll_counts:
        roll_counts[chat_id] = 0
    current_index = roll_counts[chat_id] % len(WIN_PATTERN)
    target_type = WIN_PATTERN[current_index]
    roll_counts[chat_id] += 1
    return random.choice([2, 4, 6]) if target_type == 'E' else random.choice([1, 3, 5])

# --- 3. COMMANDS ---

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    message_id = update.message.message_id

    # Admin Check
    try:
        user_stat = await context.bot.get_chat_member(chat_id, user_id)
        if user_stat.status not in ["administrator", "creator"]:
            return
    except: return

    # Result generate aur reply (No Cooldown here)
    res = get_pattern_roll(chat_id)
    await context.bot.send_message(
        chat_id=chat_id, 
        text=str(res), 
        reply_to_message_id=message_id
    )

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.message.message_id

    try:
        user_stat = await context.bot.get_chat_member(chat_id, update.effective_user.id)
        if user_stat.status not in ["administrator", "creator"]:
            return
        
        if not context.args: return
        
        user_num = context.args[0]
        suits = ["♣️", "♥️", "♦️", "♠️"]
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        deck = [f"{s}{r}" for s in suits for r in ranks]
        selected_cards = random.sample(deck, 3)
        
        for card in selected_cards:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"{user_num} cards {card}", 
                reply_to_message_id=message_id
            )
            # Bahut kam delay taaki cards order mein rahein
            time.sleep(0.05)
    except: pass

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result and result.from_user.id == OWNER_ID:
        if result.new_chat_member.status in ["left", "kicked"]:
            try:
                await context.bot.leave_chat(result.chat.id)
            except: pass

# --- 4. MAIN ---
if __name__ == '__main__':
    Thread(target=run, daemon=True).start()
    
    # concurrent_updates=True taaki multiple clicks handle ho sakein
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("show", show))
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))
    
    print("🚀 Bot is Ready: Multiple clicks allowed, but no extra results.")
    # drop_pending_updates=True zaroori hai purana kachra saaf karne ke liye
    application.run_polling(drop_pending_updates=True)
    
