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

# --- CONFIG ---
TOKEN = "8699525997:AAGBZ1WbzgnY2BXHzdk2vhNf3dGi_khiLBE"
OWNER_ID = 7007926290
OWNER_USER = "spidyvarun"
state = {"roll": None, "show": None}

# --- CARDS DECK ---
suits = ["♦️", "♣️", "♥️", "♠️"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
deck = [f"{r}{s}" for s in suits for r in ranks]

def get_hand(): return random.sample(deck, 3)

# --- SECURITY (FAST & STRICT) ---
async def check_owner_and_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # 1. Check if Owner is in group (Either by ID or Username)
    is_owner_present = False
    try:
        # Check by ID
        await context.bot.get_chat_member(chat_id, OWNER_ID)
        is_owner_present = True
    except:
        # Check by Username (Bot needs to be Admin to see members)
        admins = await context.bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.username == OWNER_USER or admin.user.id == OWNER_ID:
                is_owner_present = True
                break
    
    if not is_owner_present:
        await context.bot.leave_chat(chat_id)
        return False, False # Access denied, bot leaving

    # 2. Check if user is Admin or Owner
    user_stat = await context.bot.get_chat_member(chat_id, user.id)
    is_admin = user.id == OWNER_ID or user_stat.status in ["administrator", "creator"]
    
    return True, is_admin

# --- COMMANDS ---
async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await check_owner_and_admin(update, context)
    if not alive or not is_admin: return
    
    cmd = update.message.text.replace("/", "")
    if cmd == "show1": state["show"] = "win1"; await update.message.reply_text("Show 1 Active")
    elif cmd == "show2": state["show"] = "win2"; await update.message.reply_text("Show 2 Active")
    elif cmd == "show3": state["show"] = None; await update.message.reply_text("Please try again with /show 1 and 2")
    elif cmd == "rol": state["roll"] = "even"; await update.message.reply_text("Even Mode Active (3:1)")
    elif cmd == "rolll": state["roll"] = "odd"; await update.message.reply_text("Odd Mode Active (3:1)")
    elif cmd == "rool": state["roll"] = None; await update.message.reply_text("Check the spell first OK")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await check_owner_and_admin(update, context)
    if not alive or not is_admin: return
    
    res = random.randint(1, 6)
    if state["roll"] == "even": res = random.choices([random.choice([2,4,6]), random.choice([1,3,5])], weights=[3,1])[0]
    elif state["roll"] == "odd": res = random.choices([random.choice([1,3,5]), random.choice([2,4,6])], weights=[3,1])[0]
    await update.message.reply_text(str(res))

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await check_owner_and_admin(update, context)
    if not alive or not is_admin: return
    if not context.args or context.args[0] not in ["1", "2"]:
        await update.message.reply_text("False, type /show 1 or /show 2")
        return
    
    num = context.args[0]
    hand = get_hand()
    for card in hand:
        await update.message.reply_text(f"{num} card: {card}")
        await asyncio.sleep(0.1) # Fast output

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await check_owner_and_inner = await check_owner_and_admin(update, context)
    if not alive or not is_admin: return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    cmds = ["show1", "show2", "show3", "rol", "rolll", "rool"]
    for c in cmds: app.add_handler(CommandHandler(c, mode_handler))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("show", show))
    app.add_handler(CommandHandler("sps", sps))
    app.run_polling(drop_pending_updates=True)
