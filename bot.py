import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "YOUR_TOKEN_HERE"
OWNER_ID = 7007926290

bot_state = {"roll_mode": "normal", "show_mode": "none"}
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♦️", "♣️", "♥️", "♠️"]

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def run_flask(): app.run(host='0.0.0.0', port=8080)

# Permission Check: Admin ho ya Owner, aur Owner group mein hona chahiye
async def has_permission(update, context):
    try:
        # Check if owner is present in the group
        await context.bot.get_chat_member(update.effective_chat.id, OWNER_ID)
        
        # Check if user is Owner or Group Admin
        user = update.effective_user
        if user.id == OWNER_ID:
            return True
            
        member = await context.bot.get_chat_member(update.effective_chat.id, user.id)
        return member.status in ['administrator', 'creator']
    except:
        return False

async def roll(update, context):
    if not await has_permission(update, context): return
    mode = bot_state["roll_mode"]
    if mode == "odd": res = random.choice([1, 3, 5])
    elif mode == "even": res = random.choice([2, 4, 6])
    elif mode == "even_heavy": res = random.choices([1,2,3,4,5,6], weights=[10, 25, 10, 25, 10, 20])[0]
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def show(update, context):
    if not await has_permission(update, context): return
    args = context.args
    if not args or args[0] not in ["1", "2"]:
        await update.message.reply_text("❌ Error: Invalid command! Use '/show 1' or '/show 2'")
        return
    
    val = args[0]
    mode = bot_state["show_mode"]
    pool = ["J", "Q", "K", "A"] if (mode == "win1" and val == "1") or (mode == "win2" and val == "2") else \
           ["2", "3", "4"] if (mode == "win1" and val == "2") or (mode == "win2" and val == "1") else RANKS
        
    # Teen alag-alag message bhejne ke liye loop
    for _ in range(3):
        card = f"{val} cards {random.choice(pool)}{random.choice(SUITS)}"
        await update.message.reply_text(card)

async def modes(update, context):
    if not await has_permission(update, context): return
    cmd = update.message.text
    if "/11" in cmd: bot_state["roll_mode"] = "odd"
    elif "/22" in cmd: bot_state["roll_mode"] = "even"
    elif "/33" in cmd: bot_state["roll_mode"] = "normal"
    elif "/21" in cmd: bot_state["roll_mode"] = "even_heavy"
    elif "/win11" in cmd: bot_state["show_mode"] = "win1"
    elif "/win22" in cmd: bot_state["show_mode"] = "win2"
    await update.message.reply_text(f"✅ Active: {cmd}")

async def sps(update, context):
    if not await has_permission(update, context): return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("show", show))
    app.add_handler(CommandHandler(["11", "22", "33", "21", "win11", "win22"], modes))
    app.add_handler(CommandHandler("sps", sps))
    app.run_polling()
