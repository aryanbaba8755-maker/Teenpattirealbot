import random
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
TOKEN = "8699525997:AAEkJ7ePN7RjCTvonA_WGtExPl46D8gDdM4"
OWNER_ID = 7007926290

# --- Flask Keep Alive (24/7) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive & Running 24/7"
def run_flask(): app.run(host='0.0.0.0', port=8080)
threading.Thread(target=run_flask).start()

# --- State ---
bot_state = {"roll_mode": "normal", "show_mode": "none"}
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♦️", "♣️", "♥️", "♠️"]

# --- Security Logic ---
async def is_authorized(update, context):
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. Anti-Promotion (Har message check hoga)
    if update.message and update.message.text:
        text = update.message.text.lower()
        if any(x in text for x in ["http", "t.me", "join", "channel", "promo", "bet"]):
            await update.message.delete()
            return False

    # 2. Owner Presence Check
    try:
        await context.bot.get_chat_member(chat.id, OWNER_ID)
    except:
        await context.bot.leave_chat(chat.id)
        return False
        
    # 3. Admin Check
    if user.id == OWNER_ID: return True
    member = await context.bot.get_chat_member(chat.id, user.id)
    return member.status in ['administrator', 'creator']

# --- Game Commands ---
async def roll(update, context):
    if not await is_authorized(update, context): return
    mode = bot_state["roll_mode"]
    if mode == "odd": res = random.choice([1, 3, 5])
    elif mode == "even": res = random.choice([2, 4, 6])
    elif mode == "even_heavy": res = random.choices([1,2,3,4,5,6], weights=[10, 25, 10, 25, 10, 20])[0]
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def show(update, context):
    if not await is_authorized(update, context): return
    if not context.args or context.args[0] not in ["1", "2"]:
        await update.message.reply_text("❌ Format: /show 1 or /show 2")
        return
    
    val = context.args[0]
    mode = bot_state["show_mode"]
    # Win Modes Logic
    if mode == "win1": pool = ["J", "Q", "K", "A"] if val == "1" else ["2", "3", "4"]
    elif mode == "win2": pool = ["2", "3", "4"] if val == "1" else ["J", "Q", "K", "A"]
    else: pool = RANKS
    
    cards = [f"{val} cards {random.choice(pool)}{random.choice(SUITS)}" for _ in range(3)]
    await update.message.reply_text("\n".join(cards))

async def set_modes(update, context):
    if not await is_authorized(update, context): return
    cmd = update.message.text
    if "/11" in cmd: bot_state["roll_mode"] = "odd"
    elif "/22" in cmd: bot_state["roll_mode"] = "even"
    elif "/33" in cmd: bot_state["roll_mode"] = "normal"
    elif "/21" in cmd: bot_state["roll_mode"] = "even_heavy"
    elif "/win11" in cmd: bot_state["show_mode"] = "win1"
    elif "/win22" in cmd: bot_state["show_mode"] = "win2"
    elif "/45" in cmd: bot_state["show_mode"] = "none" # Reset show mode
    await update.message.reply_text(f"✅ Mode Updated: {cmd}")

async def sps(update, context):
    if not await is_authorized(update, context): return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("show", show))
    app.add_handler(CommandHandler(["11", "22", "33", "21", "win11", "win22", "45"], set_modes))
    app.add_handler(CommandHandler("sps", sps))
    # Anti-Promotion Listener
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), lambda u, c: None))
    
    print("Bot is fully operational...")
    app.run_polling(drop_pending_updates=True)
