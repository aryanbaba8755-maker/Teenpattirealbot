import random
import os
import asyncio
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

# --- 3. COMMANDS ---

# --- RANDOM ROLL (Odd/Even Randomly) ---
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    try:
        user_stat = await context.bot.get_chat_member(chat_id, user_id)
        if user_stat.status not in ["administrator", "creator"]:
            return
    except: return

    # Ek dum random: 1 se 6 ke beech koi bhi number
    res = random.randint(1, 6)
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text=f"🎲 Roll: {res}", 
        reply_to_message_id=update.message.message_id
    )

# --- RANDOM CARDS ---
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        user_stat = await context.bot.get_chat_member(chat_id, update.effective_user.id)
        if user_stat.status not in ["administrator", "creator"]:
            return
        
        user_num = context.args[0] if context.args else "Player"
        suits = ["♣️", "♥️", "♦️", "♠️"]
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        deck = [f"{s}{r}" for s in suits for r in ranks]
        
        # 3 Cards randomly select karna
        selected_cards = random.sample(deck, 3)
        
        for card in selected_cards:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"🃏 {user_num} cards: {card}", 
                reply_to_message_id=update.message.message_id
            )
            await asyncio.sleep(0.1)
    except: pass

# --- RANDOM SPS (Stone, Paper, Scissors) ---
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        user_stat = await context.bot.get_chat_member(chat_id, update.effective_user.id)
        if user_stat.status not in ["administrator", "creator"]:
            return

        options = ["🪨 Stone", "📄 Paper", "✂️ Scissors"]
        result = random.choice(options)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎮 Result: {result}",
            reply_to_message_id=update.message.message_id
        )
    except: pass

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result and result.from_user.id == OWNER_ID:
        if result.new_chat_member.status in ["left", "kicked"]:
            try: await context.bot.leave_chat(result.chat.id)
            except: pass

# --- 4. MAIN ---
if __name__ == '__main__':
    Thread(target=run, daemon=True).start()
    
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))
    
    print("🚀 Bot is LIVE: Everything is 100% Random!")
    application.run_polling(drop_pending_updates=True)
