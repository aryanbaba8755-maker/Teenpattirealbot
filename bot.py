import random
import logging
import os
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- 1. FLASK SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online 24/7!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive():
    t = Thread(target=run); t.daemon = True; t.start()

# --- 2. CONFIG ---
logging.basicConfig(level=logging.INFO)
TOKEN = "8699525997:AAGBZ1WbzgnY2BXHzdk2vhNf3dGi_khiLBE"

modes = {"roll": "normal", "show": "random"}
suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
rank_map = {"A":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":11, "Q":12, "K":13}
DECK = [f"{s}{r}" for s in suits for r in ranks]

# --- 3. HELPERS ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_stat = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return user_stat.status in ["administrator", "creator"]
    except: return False

def get_card_value(card): return rank_map[card[2:]] if len(card) > 2 else rank_map[card[1:]]

# --- 4. COMMAND HANDLERS ---
async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    cmd = update.message.text.split()[0]
    
    if cmd == "/oddmode": modes["roll"] = "odd"; await update.message.reply_text("RAONE GAMING ZONE")
    elif cmd == "/evenmode": modes["roll"] = "even"; await update.message.reply_text("RAONE GAMING ZONE")
    elif cmd == "/show1mode": modes["show"] = "show1"; await update.message.reply_text("RAONE GAMING ZONE")
    elif cmd == "/show2mode": modes["show"] = "show2"; await update.message.reply_text("RAONE GAMING ZONE")
    elif cmd == "/normal" or cmd == "/stopshowmode":
        modes["roll"] = "normal"; modes["show"] = "random"
        await update.message.reply_text("RAONE GAMING")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if modes["roll"] == "odd": res = random.choices([1, 3, 5, 2, 4, 6], weights=[3, 3, 3, 1, 1, 1])[0]
    elif modes["roll"] == "even": res = random.choices([2, 4, 6, 1, 3, 5], weights=[7, 7, 7, 1, 1, 1])[0]
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    
    c1 = random.sample(DECK, 3)
    c2 = random.sample(DECK, 3)
    val1 = sum(get_card_value(c) for c in c1)
    val2 = sum(get_card_value(c) for c in c2)

    if modes["show"] == "show1" and val1 <= val2: val1, val2 = val2 + random.randint(1, 5), val1
    elif modes["show"] == "show2" and val2 <= val1: val2, val1 = val1 + random.randint(1, 5), val2

    await update.message.reply_text(f"Show 1: {' '.join(c1)} (Total: {val1})\nShow 2: {' '.join(c2)} (Total: {val2})")

# --- 5. MAIN ---
if __name__ == '__main__':
    keep_alive()
    application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    
    cmds = ["oddmode", "evenmode", "normal", "show1mode", "show2mode", "stopshowmode"]
    for c in cmds: application.add_handler(CommandHandler(c, mode_handler))
    
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("show", show))
    
    print("🚀 Bot Started with Advanced Modes")
    application.run_polling(drop_pending_updates=True)
    
