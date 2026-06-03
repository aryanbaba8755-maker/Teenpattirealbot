import random, logging, os, asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Flask (24/7 Keep Alive)
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()

# Config
TOKEN = "8699525997:AAFIwWQ5JIZ1iXvhSd7G030wQz69Sns71as"
suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
DECK = [f"{s}{r}" for s in suits for r in ranks]

# Anti-Spam Lock
processing = {}

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return member.status in ['administrator', 'creator']
    except: return False

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not await is_admin(update, context):
        await update.message.reply_text("Admin nahi ho, main nikal raha hoon!")
        await context.bot.leave_chat(chat_id)
        return
    if processing.get(chat_id): return
    if not context.args: return
    
    processing[chat_id] = True
    user_num = context.args[0]
    cards = random.sample(DECK, 3)
    for card in cards:
        await update.message.reply_text(f"{update.effective_user.first_name}\n/show {user_num}\n{user_num} cards: {card}", quote=True)
        await asyncio.sleep(0.3)
    processing[chat_id] = False

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    await update.message.reply_text(str(random.randint(1, 6)), quote=True)

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]), quote=True)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(False).build()
    application.add_handler(CommandHandler("show", show))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("sps", sps))
    application.run_polling(drop_pending_updates=True)
