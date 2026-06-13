import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8699525997:AAH7VjvluYvif8Yt32IxI-wKVRa1muo7yOo"
OWNER_ID = 7007926290
OWNER_USER = "spidyvarun"

bot_state = {
    "special_mode": "3333",
    "last_commands": set()
}

RANK_ORDER = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14
}

suits = ["♦️", "♣️", "♥️", "♠️"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

async def is_owner_or_admin(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id == OWNER_ID:
        return True

    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

async def check_owner_in_group(update, context):
    chat_id = update.effective_chat.id

    try:
        owner_member = await context.bot.get_chat_member(chat_id, OWNER_ID)
        return owner_member.status not in ["left", "banned"]
    except:
        return False

async def show_result(update, context):
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return

    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.effective_chat.id)
        return

    if context.args is None or len(context.args) == 0:
        await update.message.reply_text("❌ ERROR: Must use `/show 1` or `/show 2`")
        return

    cards = []

    if bot_state["special_mode"] == "3333":
        for _ in range(3):
            rank = random.choice(ranks)
            suit = random.choice(suits)
            cards.append((rank, suit))

    elif bot_state["special_mode"] == "1111":
        arg = context.args[0].lower()
        if arg in ["1", "show"]:
            low_ranks = ["2", "3", "4", "5", "6", "7", "8"]
            for _ in range(3):
                rank = random.choice(low_ranks)
                suit = random.choice(suits)
                cards.append((rank, suit))
        else:
            high_ranks = ["9", "10", "J", "Q", "K", "A"]
            for _ in range(3):
                rank = random.choice(high_ranks)
                suit = random.choice(suits)
                cards.append((rank, suit))

    elif bot_state["special_mode"] == "2222":
        arg = context.args[0].lower()
        if arg in ["1", "show"]:
            low_ranks = ["2", "3", "4", "5", "6", "7", "8"]
            for _ in range(3):
                rank = random.choice(low_ranks)
                suit = random.choice(suits)
                cards.append((rank, suit))
        else:
            high_ranks = ["9", "10", "J", "Q", "K", "A"]
            for _ in range(3):
                rank = random.choice(high_ranks)
                suit = random.choice(suits)
                cards.append((rank, suit))

    reply = ""
    for rank, suit in cards:
        reply += f"1 cards {rank} {suit}
"

    await update.message.reply_text(reply)

async def roll_logic(update, context):
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return

    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.effective_chat.id)
        return

    command = update.message.text.split()[0].lower()
    cmd_key = f"{command}:{update.message.message_id}"

    if cmd_key in bot_state["last_commands"]:
        return
    bot_state["last_commands"].add(cmd_key)

    dice = random.randint(1, 6)
    await update.message.reply_text(str(dice))

async def sps(update, context):
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return

    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.effective_chat.id)
        return

    result = random.choice(["Stone", "Paper", "Scissors"])
    await update.message.reply_text(f"🎮 Result: {result}")

async def set_special_mode_1111(update, context):
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return

    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.effective_chat.id)
        return

    bot_state["special_mode"] = "1111"
    await update.message.reply_text("✅ Mode set to: /1111 (show1=BIG, show2=SMALL)")

async def set_special_mode_2222(update, context):
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return

    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.effective_chat.id)
        return

    bot_state["special_mode"] = "2222"
    await update.message.reply_text("✅ Mode set to: /2222 (show1=SMALL, show2=BIG)")

async def set_special_mode_3333(update, context):
    if not await is_owner_or_admin(update, context):
        await update.message.reply_text("❌ Only owner/admin can use this command")
        return

    if not await check_owner_in_group(update, context):
        await update.message.reply_text("❌ Owner is not in this group. Bot leaving.")
        await context.bot.leave_chat(update.effective_chat.id)
        return

    bot_state["special_mode"] = "3333"
    await update.message.reply_text("✅ Mode set to: /3333 (Normal Random)")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("show", show_result))
    application.add_handler(CommandHandler(["roll", "rol", "rolll"], roll_logic))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(CommandHandler("1111", set_special_mode_1111))
    application.add_handler(CommandHandler("2222", set_special_mode_2222))
    application.add_handler(CommandHandler("3333", set_special_mode_3333))

    application.run_polling()

if __name__ == "__main__":
    main()
