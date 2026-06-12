import random
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAGBZ1WbzgnY2BXHzdk2vhNf3dGi_khiLBE"
OWNER_ID = 7007926290
OWNER_USER = "spidyvarun"
state = {"roll_mode": None}

# --- SECURITY CHECK ---
async def security_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        # Check if Owner is in the group
        is_owner_present = any(a.user.id == OWNER_ID or a.user.username == OWNER_USER for a in admins)
        
        if not is_owner_present:
            await context.bot.leave_chat(chat_id)
            return False, False
        
        # Check if user is Admin or Owner
        user = update.effective_user
        user_stat = await context.bot.get_chat_member(chat_id, user.id)
        is_admin = (user.id == OWNER_ID) or (user_stat.status in ["administrator", "creator"])
        return True, is_admin
    except:
        return False, False

# --- COMMANDS ---
async def handle_roll_modes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await security_check(update, context)
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
        await update.message.reply_text("Random Mode Active.")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await security_check(update, context)
    if not alive or not is_admin: return
    
    if state["roll_mode"] == "even": res = random.choice([2, 4, 6])
    elif state["roll_mode"] == "odd": res = random.choice([1, 3, 5])
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await security_check(update, context)
    if not alive or not is_admin: return
    
    suits = ["♦️", "♣️", "♥️", "♠️"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    deck = [f"{r}{s}" for s in suits for r in ranks]
    cards = random.sample(deck, 3)
    
    for card in cards:
        await update.message.reply_text(card)
        await asyncio.sleep(0.1)

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await security_check(update, context)
    if not alive or not is_admin: return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

if __name__ == '__main__':
    bot = ApplicationBuilder().token(TOKEN).build()
    
    # Register Commands
    for cmd in ["rol", "rolll", "stop"]: bot.add_handler(CommandHandler(cmd, handle_roll_modes))
    bot.add_handler(CommandHandler("roll", roll))
    bot.add_handler(CommandHandler("show", show))
    bot.add_handler(CommandHandler("sps", sps))
    
    bot.run_polling()
