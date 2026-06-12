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
state = {"roll": None, "show": None}

def get_hand(): return random.sample(deck, 3)
def get_hand_strength(hand): return sum(rank_val[c[:-1]] for c in hand)

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
            
        user_stat = await context.bot.get_chat_member(chat_id, user.id)
        is_admin = user.id == OWNER_ID or user_stat.status in ["administrator", "creator"]
        return True, is_admin
    except: return False, False

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
    h1, h2 = get_hand(), get_hand()
    if state["show"] == "win1":
        while get_hand_strength(h1) <= get_hand_strength(h2): h1, h2 = get_hand(), get_hand()
    elif state["show"] == "win2":
        while get_hand_strength(h2) <= get_hand_strength(h1): h1, h2 = get_hand(), get_hand()
    
    target = h1 if num == "1" else h2
    for card in target:
        # Format fix: "1 cards Q♦️"
        await update.message.reply_text(f"{num} cards {card}")
        await asyncio.sleep(0.05) # Fast delivery
async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await check_owner_and_admin(update, context)
    if not alive or not is_admin: return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

if name == 'main':
    app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    for c in ["show1", "show2", "show3", "rol", "rolll", "rool"]: app.add_handler(CommandHandler(c, mode_handler))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("show", show))
    app.add_handler(CommandHandler("sps", sps))
    app.run_polling(drop_pending_updates=True)
