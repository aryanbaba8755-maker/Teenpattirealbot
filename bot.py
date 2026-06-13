import random
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAH7VjvluYvif8Yt32IxI-wKVRa1muo7yOo"
OWNER_ID = 7007926290
OWNER_USER = "spidyvarun"

bot_state = {
    "special_mode": "3333",  # Default: normal random
    "last_commands": set()  # Track used commands for single reply
}

RANK_ORDER = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
suits = ["♦️", "♣️", "♥️", "♠️"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

async def is_owner_or_admin(update, context):
    """Check if user is owner or admin"""
    user_id = update.effective_user.id
    chat_id = update.chat_id
    
    if user_id == OWNER_ID:
        return True
    
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

async def check_owner_in_group(update, context):
    """Check if owner is in group - bot leaves if not"""
    chat_id = update.chat_id
    
    try:
        owner_member = await context.bot.get_chat_member(chat_id, OWNER_ID)
        return owner_member.status not in ["left", "banned"]
    except:
        return False

async def show_result(update, context):
    """Show cards - requires argument"""
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return
    
    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(chat_id)
        return
    
    # Check if argument provided
    if context.args is None or len(context.args) == 0:
        await update.message.reply_text("❌ ERROR: Must use `/show 1` or `/show 2`")
        return
    
    # Any argument works - same reply format
    cards = []
    
    if bot_state["special_mode"] == "3333":  # Normal random
        for _ in range(3):
            rank = random.choice(ranks)
            suit = random.choice(suits)
            cards.append((rank, suit))
    
    elif bot_state["special_mode"] == "1111":  # show1=BIG, show2=SMALL
        arg = context.args[0].lower()
        if arg in ["1", "show"]:  # Low cards (2-8)
            low_ranks = ["2", "3", "4", "5", "6", "7", "8"]
            for _ in range(3):
                rank = random.choice(low_ranks)
                suit = random.choice(suits)
                cards.append((rank, suit))
        else:  # High cards (9-A)
            high_ranks = ["9", "10", "J", "Q", "K", "A"]
            for _ in range(3):
                rank = random.choice(high_ranks)
                suit = random.choice(suits)
                cards.append((rank, suit))
    
    elif bot_state["special_mode"] == "2222":  # show1=SMALL, show2=BIG
        arg = context.args[0].lower()
        if arg in ["1", "show"]:  # Low cards (2-8)
            low_ranks = ["2", "3", "4", "5", "6", "7", "8"]
            for _ in range(3):
                rank = random.choice(low_ranks)
                suit = random.choice(suits)
                cards.append((rank, suit))
        else:  # High cards (9-A)
            high_ranks = ["9", "10", "J", "Q", "K", "A"]
            for _ in range(3):
                rank = random.choice(high_ranks)
                suit = random.choice(suits)
                cards.append((rank, suit))
    
    # NEW FORMAT - ✅ FIXED: 
 as escape character
    reply = ""
    for i, (rank, suit) in cards:
        reply += f"1 cards {rank} {suit}
"
    
    await update.message.reply_text(reply)

async def roll_logic(update, context):
    """Roll dice - NORMAL numbers (1-6)"""
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return
    
    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.chat_id)
        return
    
    command = update.message.text.split()[0].lower()
    
    # Check for single reply
    cmd_key = f"{command}:{update.message.message_id}"
    if cmd_key in bot_state["last_commands"]:
        return
    bot_state["last_commands"].add(cmd_key)
    
    # Normal random number 1-6
    dice = random.randint(1, 6)
    await update.message.reply_text(str(dice))

async def sps(update, context):
    """Stone Paper Scissors"""
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return
    
    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.chat_id)
        return
    
    choices = ["Stone", "Paper", "Scissors"]
    result = random.choice(choices)
    await update.message.reply_text(f"🎮 Result: {result}")

async def set_special_mode_1111(update, context):
    """Set mode 1111"""
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return
    
    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.chat_id)
        return
    
    bot_state["special_mode"] = "1111"
    await update.message.reply_text("✅ Mode set to: `/1111` (show1=BIG, show2=SMALL)")

async def set_special_mode_2222(update, context):
    """Set mode 2222"""
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return
    
    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.chat_id)
        return
    
    bot_state["special_mode"] = "2222"
    await update.message.reply_text("✅ Mode set to: `/2222` (show1=SMALL, show2=BIG)")

async def set_special_mode_3333(update, context):
    """Set mode 3333 (default)"""
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return
    
    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.chat_id)
        return
    
    bot_state["special_mode"] = "3333"
    await update.message.reply_text("✅ Mode set to: `/3333` (Normal Random)")

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("show", show_result))
    application.add_handler(CommandHandler(["roll", "rol", "rolll"], roll_logic))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(CommandHandler("1111", set_special_mode_1111))
    application.add_handler(CommandHandler("2222", set_special_mode_2222))
    application.add_handler(CommandHandler("3333", set_special_mode_3333))
    
    application.run_polling()
