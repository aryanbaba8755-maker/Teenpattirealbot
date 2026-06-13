import logging
import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
TOKEN = "8699525997:AAH7VjvluYvif8Yt32IxI-wKVRa1muo7yOo"
OWNER_ID = 7007926290

# State
bot_state = {"roll_mode": "normal", "show_mode": "none"}
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♦️", "♣️", "♥️", "♠️"]

# Flask Keep-Alive
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Active!"
def run_flask(): app.run(host='0.0.0.0', port=8080)

# --- Helpers ---
def is_admin(update):
    return update.effective_user.id == OWNER_ID

async def admin_check(update, context):
    # Auto-leave logic
    chat_member = await context.bot.get_chat_member(update.effective_chat.id, OWNER_ID)
    if chat_member.status in ['left', 'kicked']:
        await update.effective_chat.leave()
        return False
    return is_admin(update)

# --- Commands ---
async def roll(update, context):
    if not await admin_check(update, context): return
    mode = bot_state["roll_mode"]
    
    if mode == "odd": res = random.choice([1, 3, 5])
    elif mode == "even": res = random.choice([2, 4, 6])
    elif mode == "even_heavy": res = random.choices([1,2,3,4,5,6], weights=[10, 25, 10, 25, 10, 20])[0]
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def show_cards(update, context):
    if not await admin_check(update, context): return
    args = context.args
    if not args or args[0] not in ["1", "2"]:
        await update.message.reply_text("❌ Error: Invalid format! Use '/show 1' or '/show 2'")
        return
    
    val = args[0]
    mode = bot_state["show_mode"]
    
    # Logic for Win1/Win2
    if mode == "win1":
        pool = ["J", "Q", "K", "A"] if val == "1" else ["2", "3", "4"]
    elif mode == "win2":
        pool = ["2", "3", "4"] if val == "1" else ["J", "Q", "K", "A"]
    else:
        pool = RANKS
        
    cards = [f"{val} cards {random.choice(pool)}{random.choice(SUITS)}" for _ in range(3)]
    await update.message.reply_text("\n".join(cards))

async def set_mode(update, context):
    if not await admin_check(update, context): return
    cmd = update.message.text
    if "/11" in cmd: bot_state["roll_mode"] = "odd"
    elif "/22" in cmd: bot_state["roll_mode"] = "even"
    elif "/33" in cmd: bot_state["roll_mode"] = "normal"
    elif "/21" in cmd: bot_state["roll_mode"] = "even_heavy"
    elif "/win11" in cmd: bot_state["show_mode"] = "win1"
    elif "/win22" in cmd: bot_state["show_mode"] = "win2"
    await update.message.reply_text(f"✅ Mode Updated: {cmd}")

async def sps(update, context):
    if not await admin_check(update, context): return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("show", show_cards))
    app.add_handler(CommandHandler(["11", "22", "33", "21", "win11", "win22"], set_mode))
    app.add_handler(CommandHandler("sps", sps))
    
    app.run_polling()
    
