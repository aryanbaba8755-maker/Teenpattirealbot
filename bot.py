import random
import logging
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- 1. FLASK SERVER SETUP (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live and Running 24/7!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. CONFIG ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

OWNER_ID = 7007926290
TOKEN = "8699525997:AAG1TqOezIL1tl-Qch9bDKEVmlwW9dEkWqU"

suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# --- 3. HELPER FUNCTION ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        user_stat = await context.bot.get_chat_member(chat_id, user_id)
        return user_stat.status in ["administrator", "creator"]
    except:
        return False

# --- 4. COMMAND HANDLERS ---

# /roll Command (Sirf Number reply karega)
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        number = random.randint(1, 6)
        # reply_to_message_id se bilkul screenshot jaisa reply aayega
        await update.message.reply_text(str(number))

# /sps Command
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, context):
        options = ["Stone", "Paper", "Scissors"]
        result = random.choice(options)
        await update.message.reply_text(result)

# /show Command
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        # Owner check logic
        owner_stat = await context.bot.get_chat_member(chat_id, OWNER_ID)
        if owner_stat.status not in ["administrator", "creator"]:
            await context.bot.leave_chat(chat_id)
            return

        if await is_admin(update, context):
            if not context.args:
                await update.message.reply_text("❗ Use: /show 1-100")
                return
            user_num = context.args[0]
            selected_cards = random.sample(DECK, 3)
            for card in selected_cards:
                await update.message.reply_text(f"{user_num} cards {card}")
    except Exception as e:
        logging.error(f"Error in show: {e}")

# --- 5. MAIN EXECUTION ---
if __name__ == '__main__': # Galti theek kar di (Dono side underscore)
    keep_alive()
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(CommandHandler("show", show))
    
    print("🚀 Bot is starting in clean mode...")
    application.run_polling(drop_pending_updates=True)
    
