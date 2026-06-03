import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from flask import Flask
from threading import Thread

# Config
TOKEN = '8699525997:AAGW_yxKqpFovncJC1HEOI3qSRpZeEYrSvY'
OWNER_ID = 7007926290

# Flask for keeping alive
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is alive!"

def run_flask(): app.run(host='0.0.0.0', port=8080)

# Security: Sirf Owner ki commands maanega
async def admin_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        # Agar admin nahi hai, toh kuch nahi karega (silence)
        return False
    
    # Auto-Leave check
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, OWNER_ID)
        if member.status in ['left', 'kicked']:
            await context.bot.leave_chat(update.effective_chat.id)
            return False
    except:
        pass
    return True

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await admin_only(update, context):
        await update.message.reply_text("Bot Ready!")

async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await admin_only(update, context):
        cmd = context.args
        val = cmd[0] if cmd else "Result"
        
        suits = ['♥️', '♦️', '♠️', '♣️']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        # 3 random cards
        cards = [f"{random.choice(suits)}{random.choice(ranks)}" for _ in range(3)]
        await update.message.reply_text(f"Result for {val}:\n{' '.join(cards)}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await admin_only(update, context):
        await update.message.reply_text(str(random.randint(1, 6)))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await admin_only(update, context):
        await update.message.reply_text(random.choice(['Stone', 'Paper', 'Scissors']))

if __name__ == '__main__':
    Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('show', show_command))
    application.add_handler(CommandHandler('roll', roll))
    application.add_handler(CommandHandler('sps', sps))
    
    print("Bot is running securely...")
    application.run_polling(drop_pending_updates=True)
