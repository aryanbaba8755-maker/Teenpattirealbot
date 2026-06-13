import random
import asyncio
import os
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAHTja1rJ4RwKPd3QV-Ye8hg-VnE19kTOSo"
OWNER_ID = 7007926290
OWNER_USER = "spidyvarun"

# State management
state = {"roll_mode": None} # None, "even", "odd"

# Teen Patti Ranks (Value wise)
RANK_ORDER = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
suits = ["♦️", "♣️", "♥️", "♠️"]
deck = [(r, s) for s in suits for r in RANK_ORDER.keys()]

# --- SECURITY ---
async def security_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        is_owner_present = any(a.user.id == OWNER_ID or a.user.username == OWNER_USER for a in admins)
        if not is_owner_present:
            await context.bot.leave_chat(chat_id)
            return False
        
        user_stat = await context.bot.get_chat_member(chat_id, user.id)
        return user.id == OWNER_ID or user_stat.status in ["administrator", "creator"]
    except:
        return False

# --- COMMANDS ---
async def handle_roll_modes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    cmd = update.message.text.lstrip("/").lower()
    if cmd == "rol":
        state["roll_mode"] = "even"
        await update.message.reply_text("✅ Even Mode Active (2, 4, 6)")
    elif cmd == "rolll":
        state["roll_mode"] = "odd"
        await update.message.reply_text("✅ Odd Mode Active (1, 3, 5)")
    elif cmd == "normal":
        state["roll_mode"] = None
        await update.message.reply_text("✅ Normal Mode Active (Random 1-6)")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    if state["roll_mode"] == "even": res = random.choice([2, 4, 6])
    elif state["roll_mode"] == "odd": res = random.choice([1, 3, 5])
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    cmd = update.message.text.lstrip("/").lower()
    
    # Selection logic: /show 1 (Low) vs /show 2 (High)
    if "1" in cmd:
        subset = [c for c in deck if RANK_ORDER[c[0]] <= 8]
    else:
        subset = [c for c in deck if RANK_ORDER[c[0]] > 8]
        
    cards = random.sample(subset, 3)
    for card in cards:
        await update.message.reply_text(f"1 cards {card[0]} {card[1]}")
        await asyncio.sleep(0.1)

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

# --- FLASK KEEP ALIVE ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online"
def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

if __name__ == '__main__':
    keep_alive()
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler(["rol", "rolll", "normal"], handle_roll_modes))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler(["show1", "show2"], show))
    application.add_handler(CommandHandler("sps", sps))
    application.run_polling()
