import random
import logging
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler

# --- 1. FLASK SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Live with Winning Pattern!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- 2. CONFIG ---
logging.basicConfig(level=logging.INFO)
OWNER_ID = 7007926290
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# Anti-Extra Trigger Lock
processing_chats = set()

# --- 3. PATTERN LOGIC SETUP ---
# Aapka pattern: 3 Odd, 2 Even, 1 Odd, 4 Even, 2 Odd, 2 Even, 1 Odd, 3 Even, 2 Odd
# 'O' = Odd (1, 3, 5), 'E' = Even (2, 4, 6)
WIN_PATTERN = (['O']*3 + ['E']*2 + ['O']*1 + ['E']*4 + ['O']*2 + ['E']*2 + ['O']*1 + ['E']*3 + ['O']*2)
# Round counter
roll_counts = {}

def get_pattern_roll(chat_id):
    if chat_id not in roll_counts:
        roll_counts[chat_id] = 0
    
    current_index = roll_counts[chat_id] % len(WIN_PATTERN)
    target_type = WIN_PATTERN[current_index]
    
    roll_counts[chat_id] += 1 # Agle round ke liye count badhao
    
    if target_type == 'E':
        return random.choice([2, 4, 6])
    else:
        return random.choice([1, 3, 5])

# --- 4. HELPERS ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_stat = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return user_stat.status in ["administrator", "creator"]
    except: return False

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result and result.from_user.id == OWNER_ID:
        if result.new_chat_member.status in ["left", "kicked"]:
            try:
                await context.bot.leave_chat(result.chat.id)
            except: pass

# --- 5. COMMANDS ---

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in processing_chats: return
    
    if await is_admin(update, context):
        try:
            processing_chats.add(chat_id)
            # Pattern se number nikalna
            res = get_pattern_roll(chat_id)
            await update.message.reply_text(str(res))
        finally:
            processing_chats.discard(chat_id)

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in processing_chats: return
    if await is_admin(update, context):
        if not context.args: return
        try:
            processing_chats.add(chat_id)
            user_num = context.args[0]
            selected_cards = random.sample(DECK, 3)
            for card in selected_cards:
                await update.message.reply_text(f"{user_num} cards {card}")
                time.sleep(0.08)
        finally:
            time.sleep(0.3)
            processing_chats.discard(chat_id)

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        res = random.choice(["Stone", "Paper", "Scissors"])
        await update.message.reply_text(res)

# --- 6. MAIN ---
if __name__ == '__main__':
    Thread(target=run, daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(False).build()
    
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))
    
    print("🚀 Pattern Script Active: Even will win in long run.")
    application.run_polling(drop_pending_updates=True)
