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
def home(): return "Bot is Online 24/7!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
Thread(target=run, daemon=True).start()

# --- CARDS CONFIG ---
suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
rank_val = {r: i for i, r in enumerate(ranks, 2)}

# --- CONFIG ---
TOKEN = "8699525997:AAGBZ1WbzgnY2BXHzdk2vhNf3dGi_khiLBE"
OWNER_ID = 7007926290
state = {"roll": None, "show": None}

def get_hand(): return random.sample([f"{s}{r}" for s in suits for r in ranks], 3)
def get_hand_strength(hand): return sum(rank_val[c[2:] if len(c) > 2 else c[1:]] for c in hand)

# --- SECURITY ---
async def check_admin_and_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        await context.bot.get_chat_member(chat_id, OWNER_ID)
    except:
        await context.bot.leave_chat(chat_id)
        return False
    try:
        user_stat = await context.bot.get_chat_member(chat_id, user_id)
        return user_id == OWNER_ID or user_stat.status in ["administrator", "creator"]
    except: return False

# --- COMMANDS ---
async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_and_owner(update, context): return
    cmd = update.message.text.replace("/", "")
    if cmd == "show1": state["show"] = "win1"; await update.message.reply_text("Show 1 Mode Active")
    elif cmd == "show2": state["show"] = "win2"; await update.message.reply_text("Show 2 Mode Active")
    elif cmd == "show3": state["show"] = None; await update.message.reply_text("Please try again with /show 1 and 2")
    elif cmd == "rol": state["roll"] = "even"; await update.message.reply_text("Even Mode Active (3:1)")
    elif cmd == "rolll": state["roll"] = "odd"; await update.message.reply_text("Odd Mode Active (3:1)")
    elif cmd == "rool": state["roll"] = None; await update.message.reply_text("Check the spell first OK")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_and_owner(update, context): return
    even, odd = [2, 4, 6], [1, 3, 5]
    if state["roll"] == "even": res = random.choices([random.choice(even), random.choice(odd)], weights=[3, 1])[0]
    elif state["roll"] == "odd": res = random.choices([random.choice(odd), random.choice(even)], weights=[3, 1])[0]
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_and_owner(update, context): return
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
        await update.message.reply_text(f"{num} card: {card}")
        await asyncio.sleep(0.5)

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin_and_owner(update, context): return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

if __name__ == '__main__':
    app_builder = ApplicationBuilder().token(TOKEN).build()
    cmds = ["show1", "show2", "show3", "rol", "rolll", "rool"]
    for c in cmds: app_builder.add_handler(CommandHandler(c, mode_handler))
    app_builder.add_handler(CommandHandler("roll", roll))
    app_builder.add_handler(CommandHandler("show", show))
    app_builder.add_handler(CommandHandler("sps", sps))
    app_builder.run_polling()
