import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

TOKEN = '8699525997:AAGW_yxKqpFovncJC1HEOI3qSRpZeEYrSvY'
OWNER_ID = 7007926290

# Permission check function
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # 1. Check Owner/Admin status
    member = await context.bot.get_chat_member(chat_id, user_id)
    is_admin = member.status in ['creator', 'administrator']
    is_owner = (user_id == OWNER_ID)
    
    if not (is_admin or is_owner):
        return False # Ignore command

    # 2. Check if Owner is still in group (Auto-leave logic)
    try:
        await context.bot.get_chat_member(chat_id, OWNER_ID)
    except:
        await context.bot.leave_chat(chat_id)
        return False
        
    return True

# Commands
async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context): return
    
    cmd = context.args
    val = cmd[0] if cmd else "Result"
    
    suits = ['♥️', '♦️', '♠️', '♣️']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    # 3 random cards
    cards = [f"{random.choice(suits)}{random.choice(ranks)}" for _ in range(3)]
    await update.message.reply_text(f"Result for {val}:\n{' '.join(cards)}")

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context): return
    await update.message.reply_text(str(random.randint(1, 6)))

# Main setup
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('show', show_command))
    application.add_handler(CommandHandler('roll', roll))
    
    print("Bot is running with Admin/Owner security...")
    application.run_polling(drop_pending_updates=True)
