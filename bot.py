import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8699525997:AAHTja1rJ4RwKPd3QV-Ye8hg-VnE19kTOSo"
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

# Anti-promotion patterns
PROMOTION_PATTERNS = [
    "telegram.me", "t.me", "telegram group", "telegram channel",
    "join telegram", "whatsapp group", "whatsapp channel",
    "instagram.com", "facebook.com", "youtube.com",
    "share", "join now", "add me", "follow me",
    "click here", "http", "https",
    "₹", "rs", "money", "bet", "gambling", "casino"
]

def is_owner_or_admin(update):
    return update.effective_user.id == OWNER_ID

def contains_promotion(text):
    """Promotion detect karne ke liye"""
    if not text:
        return False
    text_lower = text.lower()
    for pattern in PROMOTION_PATTERNS:
        if pattern.lower() in text_lower:
            return True
    return False

def show_result(update, context):
    if not is_owner_or_admin(update):
        return
    
    # Anti-promotion check
    user_text = update.message.text or ""
    if contains_promotion(user_text):
        context.bot.send_message(
            update.effective_chat.id,
            "⚠️ Promotion detected! Do not share promotional content. Bot will not respond."
        )
        return
    
    special_mode = bot_state["special_mode"]
    
    if special_mode == "1111":
        low_range = (10, 13)
        high_range = (1, 8)
    elif special_mode == "2222":
        low_range = (1, 8)
        high_range = (10, 13)
    else:
        low_range = (1, 8)
        high_range = (10, 13)
    
    low_cards = [
        (ranks[random.randint(low_range[0], low_range[1])], 
         suits[random.randint(0, 3)])
        for _ in range(3)
    ]
    
    high_cards = [
        (ranks[random.randint(high_range[0], high_range[1])], 
         suits[random.randint(0, 3)])
        for _ in range(3)
    ]
    
    chat_id = update.effective_chat.id
    
    # ONE message me sab cards send karo
    cards_output = ""
    if special_mode == "1111":
        for rank, suit in low_cards:
            cards_output += f"1 cards {rank} {suit}
"
        for rank, suit in high_cards:
            cards_output += f"2 cards {rank} {suit}
"
    elif special_mode == "2222":
        for rank, suit in high_cards:
            cards_output += f"1 cards {rank} {suit}
"
        for rank, suit in low_cards:
            cards_output += f"2 cards {rank} {suit}
"
    else:
        for rank, suit in low_cards:
            cards_output += f"1 cards {rank} {suit}
"
        for rank, suit in high_cards:
            cards_output += f"2 cards {rank} {suit}
"
    
    context.bot.send_message(chat_id, cards_output)

def roll_logic(update, context):
    if not is_owner_or_admin(update):
        return
    
    # Anti-promotion check
    user_text = update.message.text or ""
    if contains_promotion(user_text):
        context.bot.send_message(
            update.effective_chat.id,
            "⚠️ Promotion detected! Do not share promotional content. Bot will not respond."
        )
        return
    
    number = random.randint(1, 6)
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, str(number))

def sps(update, context):
    if not is_owner_or_admin(update):
        return
    
    # Anti-promotion check
    user_text = update.message.text or ""
    if contains_promotion(user_text):
        context.bot.send_message(
            update.effective_chat.id,
            "⚠️ Promotion detected! Do not share promotional content. Bot will not respond."
        )
        return
    
    choices = ["Stone", "Paper", "Scissors"]
    choice = random.choice(choices)
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id, choice)

def set_special_mode_1111(update, context):
    if not is_owner_or_admin(update):
        return
    bot_state["special_mode"] = "1111"

def set_special_mode_2222(update, context):
    if not is_owner_or_admin(update):
        return
    bot_state["special_mode"] = "2222"

def set_special_mode_3333(update, context):
    if not is_owner_or_admin(update):
        return
    bot_state["special_mode"] = "3333"

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
