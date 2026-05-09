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

# Double reply protection
last_processed_time = {}

# Cards & SPS Setup (Plain Text)
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suits = ["♣️", "♥️", "♦️", "♠️"]
ALL_CARDS = [f"{s}{r}" for s in suits for r in ranks]
SPS_OPTIONS = ["Stone", "Paper", "Scissors"] # Emojis hata diye

# --- FUNCTIONS ---

# 1. SHOW Command (3 alag messages bina kisi extra text ke)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_num = context.args[0] if context.args else "1"
        res_cards = random.sample(ALL_CARDS, 3)
        
        for card in res_cards:
            text = f"{user_num} cards {card}"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
            time.sleep(0.2)
            
    except Exception as e:
        print(f"Show Error: {e}")

# 2. ROLL Command (Sirf Number)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    curr_time = time.time()

    if chat_id in last_processed_time and (curr_time - last_processed_time[chat_id]) < 0.4:
        return
    
    last_processed_time[chat_id] = curr_time
    num = random.randint(1, 6)
    # Sirf number bhejega, bina dice emoji ke
    await update.message.reply_text(str(num))

# 3. SPS Command (Sirf Text)
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    curr_time = time.time()

    if chat_id in last_processed_time and (curr_time - last_processed_time[chat_id]) < 0.4:
        return
    
    last_processed_time[chat_id] = curr_time
    choice = random.choice(SPS_OPTIONS)
    # Sirf "Stone", "Paper" ya "Scissors" bhejega
    await update.message.reply_text(choice)

# 4. Auto-Leave Logic
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result or result.from_user.id != OWNER_ID:
        return

    if result.new_chat_member.status in ["left", "kicked"]:
        try:
            await context.bot.leave_chat(result.chat.id)
        except Exception as e:
            print(f"Leave Error: {e}")

# --- FLASK SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Online"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- MAIN ---
if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()

    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))
    
    print("Bot Running (No Emojis)...")
    application.run_polling(drop_pending_updates=True)
    
