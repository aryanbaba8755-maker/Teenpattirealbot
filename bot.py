import random
import os
import time
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChatMemberHandler

# --- CONFIG ---
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU" 
OWNER_ID = 1869599187  # Is ID ke nikalte hi bot left kar dega

# Rate Limit Tracker (Double message rokne ke liye)
last_processed_time = {}

# Cards Setup
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]

# --- FUNCTIONS ---

# 1. Show Command (Random Cards)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_num = context.args[0] if context.args else "1"
    res_cards = random.sample(ALL_CARDS, 3)
    msg = f"User {user_num} Cards:\n" + "\n".join(res_cards)
    await update.message.reply_text(msg)

# 2. Roll Command (Ab Sabke Liye Pura Random)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    curr_time = time.time()

    # Double reply protection (0.8 seconds ka gap)
    if chat_id in last_processed_time:
        if curr_time - last_processed_time[chat_id] < 0.8:
            return
    
    last_processed_time[chat_id] = curr_time
    
    # 100% Pure Random Roll
    num = random.randint(1, 6)
    await update.message.reply_text(f"🎲 {num}")

# 3. Auto-Leave Logic (Owner ke nikalte hi Bot bhi niklega)
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return

    user_id = result.from_user.id
    # Agar owner (Special ID) ne group chhoda ya use nikala gaya
    if user_id == OWNER_ID:
        if result.new_chat_member.status in ["left", "kicked"]:
            await context.bot.leave_chat(result.chat.id)
            print(f"Owner left {result.chat.id}, so I also left.")

# --- FLASK SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- MAIN ---
if __name__ == '__main__':
    # Start Flask
    Thread(target=run_flask, daemon=True).start()

    # Build Bot
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    
    # Ye handler owner ke movement par nazar rakhega
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))
    
    print("Bot chalu ho gaya hai...")
    
    # drop_pending_updates=True se purane dabe hue messages reply nahi karenge
    application.run_polling(drop_pending_updates=True)
