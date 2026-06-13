import random
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAHTja1rJ4RwKPd3QV-Ye8hg-VnE19kTOSo"
OWNER_ID = 7007926290
OWNER_USER = "spidyvarun"

# State management
bot_state = {"show_mode": "1"} 

# Teen Patti Ranks
RANK_ORDER = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
suits = ["♦️", "♣️", "♥️", "♠️"]
deck = [(r, s) for s in suits for r in RANK_ORDER.keys()]

# --- SECURITY ---
async def security_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        is_owner_present = any(a.user.id == OWNER_ID or a.user.username == OWNER_USER for a in admins)
        if not is_owner_present:
            await context.bot.leave_chat(chat_id)
            return False
        
        user_stat = await context.bot.get_chat_member(chat_id, user.id)
        return user.id == OWNER_ID or user_stat.status in ["administrator", "creator"]
    except: return False

# --- COMMANDS ---
async def set_show_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    cmd = update.message.text.lower()
    if "show1" in cmd:
        bot_state["show_mode"] = "1"
        await update.message.reply_text("✅ Mode Active: Show 1 (Low Cards)")
    elif "show2" in cmd:
        bot_state["show_mode"] = "2"
        await update.message.reply_text("✅ Mode Active: Show 2 (High Cards)")

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    
    # Check if extra argument exists, agar sirf /show hai toh error
    if len(context.args) > 0:
        await update.message.reply_text("❌ Error: Sirf '/show' likhein. Mode set karne ke liye /show1 ya /show2 use karein.")
        return
        
    if bot_state["show_mode"] == "2":
        subset = [c for c in deck if RANK_ORDER[c[0]] > 8]
    else:
        subset = [c for c in deck if RANK_ORDER[c[0]] <= 8]
        
    cards = random.sample(subset, 3)
    res = "\n".join([f"{c[0]} {c[1]}" for c in cards])
    await update.message.reply_text(f"Cards Result:\n{res}")

async def roll_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    cmd = update.message.text.lower()
    if "rol" in cmd and "rolll" not in cmd: res = random.choice([2, 4, 6])
    elif "rolll" in cmd: res = random.choice([1, 3, 5])
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler(["show1", "show2"], set_show_mode))
    application.add_handler(CommandHandler("show", show_result))
    application.add_handler(CommandHandler(["roll", "rol", "rolll"], roll_logic))
    application.add_handler(CommandHandler("sps", sps))
    
    application.run_polling()
