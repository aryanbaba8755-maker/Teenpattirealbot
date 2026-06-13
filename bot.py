import random
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "YOUR_NEW_TOKEN_HERE"  # Yahan naya token daalein
OWNER_ID = 7007926290
OWNER_USER = "spidyvarun"
state = {"roll_mode": None}

# --- SECURITY CHECK ---
async def security_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        # Owner check
        is_owner_present = any(a.user.id == OWNER_ID or a.user.username == OWNER_USER for a in admins)
        if not is_owner_present:
            await context.bot.leave_chat(chat_id)
            return False, False
            
        # Admin/Owner access check
        user_stat = await context.bot.get_chat_member(chat_id, user.id)
        is_admin = user.id == OWNER_ID or user_stat.status in ["administrator", "creator"]
        return True, is_admin
    except:
        return False, False

# --- COMMANDS ---
async def handle_roll_modes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await security_check(update, context)
    if not alive or not is_admin: return
    
    cmd = update.message.text.lstrip("/").lower()
    if cmd in ["rol", "rool"]: # Dono command handled
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
    
    if not context.args:
        await update.message.reply_text("Example: /show 5")
        return
    
    num = context.args[0]
    suits = ["♦️", "♣️", "♥️", "♠️"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    deck = [f"{r}{s}" for s in suits for r in ranks]
    cards = random.sample(deck, 3)
    
    # 3 cards ek hi message mein
    result = "\n".join([f"{num} cards {card}" for card in cards])
    await update.message.reply_text(f"Result for {num}:\n{result}")

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    alive, is_admin = await security_check(update, context)
    if not alive or not is_admin: return
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

if __name__ == '__main__':
    bot = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    bot.add_handler(CommandHandler(["rol", "rool", "rolll", "stop"], handle_roll_modes))
    bot.add_handler(CommandHandler("roll", roll))
    bot.add_handler(CommandHandler("show", show))
    bot.add_handler(CommandHandler("sps", sps))
    
    print("Bot is running...")
    bot.run_polling()
