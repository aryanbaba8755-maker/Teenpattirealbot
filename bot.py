import random
import logging
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

# --- CONFIG ---
TOKEN = "8699525997:AAGBZ1WbzgnY2BXHzdk2vhNf3dGi_khiLBE"
OWNER_ID = 7007926290
modes = {"roll": "normal", "show": "random"}
suits = ["♣️", "♥️", "♦️", "♠️"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
rank_val = {r: i for i, r in enumerate(ranks, 2)}

def get_hand(): return random.sample([f"{s}{r}" for s in suits for r in ranks], 3)
def get_hand_strength(hand): return sum(rank_val[c[2:] if len(c) > 2 else c[1:]] for hand in [hand] for c in hand)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_stat = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return user_stat.status in ["administrator", "creator"]
    except: return False

# --- COMMANDS ---
async def mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    cmd = update.message.text.split()[0]
    
    if cmd == "/oddmode": modes["roll"] = "odd"; await update.message.reply_text("RAONE GAMING ZONE")
    elif cmd == "/evenmode": modes["roll"] = "even"; await update.message.reply_text("RAONE GAMING ZONE")
    elif cmd == "/show1mode": modes["show"] = "show1_win"; await update.message.reply_text("RAONE GAMING ZONE")
    elif cmd == "/show2mode": modes["show"] = "show2_win"; await update.message.reply_text("RAONE GAMING ZONE")
    elif cmd == "/normal": 
        modes["roll"] = "normal"; modes["show"] = "random"
        await update.message.reply_text("RAONE GAMING")
    elif cmd == "/stopshowmode": 
        modes["show"] = "random"; await update.message.reply_text("RAONE GAMING")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if modes["roll"] == "odd": res = random.choices([1, 3, 5, 2, 4, 6], weights=[3, 3, 3, 1, 1, 1])[0]
    elif modes["roll"] == "even": res = random.choices([2, 4, 6, 1, 3, 5], weights=[1, 1, 1, 7, 7, 7])[0]
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    if not context.args or context.args[0] not in ["1", "2"]:
        await update.message.reply_text("❗ Galti: Command ke saath number likhein (Ex: /show 1)")
        return

    num = context.args[0]
    hand1 = get_hand()
    hand2 = get_hand()

    # Logic: Agar show1mode on hai, to hand1 > hand2; agar show2mode on hai, to hand2 > hand1
    if modes["show"] == "show1_win":
        while get_hand_strength(hand1) <= get_hand_strength(hand2): hand1, hand2 = get_hand(), get_hand()
    elif modes["show"] == "show2_win":
        while get_hand_strength(hand2) <= get_hand_strength(hand1): hand1, hand2 = get_hand(), get_hand()

    target_hand = hand1 if num == "1" else hand2
    for card in target_hand:
        await update.message.reply_text(f"{num} cards: {card}")
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    app_builder = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
    cmds = ["oddmode", "evenmode", "normal", "show1mode", "show2mode", "stopshowmode"]
    for c in cmds: app_builder.add_handler(CommandHandler(c, mode_handler))
    app_builder.add_handler(CommandHandler("roll", roll))
    app_builder.add_handler(CommandHandler("show", show))
    app_builder.run_polling(drop_pending_updates=True)
