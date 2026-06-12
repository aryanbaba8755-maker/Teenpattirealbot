import random
import asyncio
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- FLASK KEEP ALIVE ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
Thread(target=run, daemon=True).start()

# --- CARDS CONFIG ---
suits = ["♦️", "♣️", "♥️", "♠️"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
# Card format: Rank + Suit (e.g., Q♦️)
deck = [f"{r}{s}" for s in suits for r in ranks]
rank_val = {r: i for i, r in enumerate(ranks, 2)}


# --- CONFIG ---
TOKEN = "8699525997:AAGBZ1WbzgnY2BXHzdk2vhNf3dGi_khiLBE"
OWNER_ID = 7007926290
OWNER_USER = "spidyvarun"
state = {"roll_mode": None} 

# --- SECURITY ---
async def check_owner_and_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        # Owner check by ID or Username
        is_owner_present = any(a.user.id == OWNER_ID or a.user.username == OWNER_USER for a in admins)
        
        if not is_owner_present:
            await context.bot.leave_chat(chat_id)
            return False, False
            
# --- ROLL COMMANDS ---
async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await check_owner_and_admin(update, context)
    if not alive or not is_admin: return
    
    cmd = update.message.text.replace("/", "")
    if cmd == "rol":
        state["roll_mode"] = "even"
        await update.message.reply_text("Even Mode Active (2, 4, 6)")
    elif cmd == "rolll":
        state["roll_mode"] = "odd"
        await update.message.reply_text("Odd Mode Active (1, 3, 5)")
    elif cmd == "stop":
        state["roll_mode"] = None
        await update.message.reply_text("Roll Mode Stopped. Random enabled.")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await check_owner_and_admin(update, context)
    if not alive or not is_admin: return
    
    if state["roll_mode"] == "even": res = random.choice([2, 4, 6])
    elif state["roll_mode"] == "odd": res = random.choice([1, 3, 5])
    else: res = random.randint(1, 6)
        
    await update.message.reply_text(str(res))

# --- OTHER COMMANDS ---
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await check_owner_and_admin(update, context)
    if not alive or not is_admin: return
    # Simple card draw logic
    hand = random.sample(deck, 3)
    await update.message.reply_text(f"Cards: {', '.join(hand)}")

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await check_owner_and_admin(update, context)
    if not alive or not is_admin: return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))
  # Format fix: "1 cards Q♦️"
        await
if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    
    # Modes
    bot_app.add_handler(CommandHandler("rol", set_mode))
    bot_app.add_handler(CommandHandler("rolll", set_mode))
    bot_app.add_handler(CommandHandler("stop", set_mode))
    # Actions
    bot_app.add_handler(CommandHandler("roll", roll))
    bot_app.add_handler(CommandHandler("show", show))
    bot_app.add_handler(CommandHandler("sps", sps))
    
    bot_app.run_polling()
