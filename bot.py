import random
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler

# --- 1. FLASK SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Fixed!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- 2. CONFIG ---
OWNER_ID = 7007926290
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

# Pattern Logic
WIN_PATTERN = (['O']*3 + ['E']*2 + ['O']*1 + ['E']*4 + ['O']*2 + ['E']*2 + ['O']*1 + ['E']*3 + ['O']*2) + ['E']*2
roll_counts = {}

# Strict Cooldown Lock: Ek user ek second mein ek hi baar click kar sakega
last_click_time = {}

def get_pattern_roll(chat_id):
    if chat_id not in roll_counts:
        roll_counts[chat_id] = 0
    current_index = roll_counts[chat_id] % len(WIN_PATTERN)
    target_type = WIN_PATTERN[current_index]
    roll_counts[chat_id] += 1
    return random.choice([2, 4, 6]) if target_type == 'E' else random.choice([1, 3, 5])

# --- 3. COMMANDS ---

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_time = time.time()

    # 1 Second Cooldown: Agar user 1 second se pehle dobara click karega toh bot ignore kar dega
    if user_id in last_click_time and (current_time - last_click_time[user_id] < 0.8):
        return 

    last_click_time[user_id] = current_time # Click time update karo

    # Check Admin
    user_stat = await context.bot.get_chat_member(update.effective_chat.id, user_id)
    if user_stat.status in ["administrator", "creator"]:
        res = get_pattern_roll(update.effective_chat.id)
        await update.message.reply_text(str(res))

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Same cooldown for show to prevent flooding
    user_id = update.effective_user.id
    current_time = time.time()
    if user_id in last_click_time and (current_time - last_click_time[user_id] < 2.0):
        return 
    last_click_time[user_id] = current_time

    user_stat = await context.bot.get_chat_member(update.effective_chat.id, user_id)
    if user_stat.status in ["administrator", "creator"]:
        if not context.args: return
        user_num = context.args[0]
        # Cards logic (Fixed to 3 cards)
        suits = ["♣️", "♥️", "♦️", "♠️"]
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        deck = [f"{s}{r}" for s in suits for r in ranks]
        selected_cards = random.sample(deck, 3)
        for card in selected_cards:
            await update.message.reply_text(f"{user_num} cards {card}")
            time.sleep(0.1)

# --- 4. MAIN ---
if __name__ == '__main__':
    Thread(target=run, daemon=True).start()
    
    # CRITICAL: concurrent_updates=False karke bot ko force kiya hai ki ek ek karke queue handle kare
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(False).build()
    
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("show", show))
    
    print("🚀 Anti-Double Click Mode Active!")
    # drop_pending_updates=True se purani bachi hui requests delete ho jayengi
    application.run_polling(drop_pending_updates=True)
