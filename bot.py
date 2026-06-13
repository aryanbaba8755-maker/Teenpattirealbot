import random
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8699525997:AAH7VjvluYvif8Yt32IxI-wKVRa1muo7yOo"
OWNER_ID = 7007926290
OWNER_USER = "spidyvarun"

# State management
bot_state = {
    "show_mode": "1",
    "special_mode": "3333",  # Default: normal random
    # 1111 = show1: BIG cards, show2: SMALL cards
    # 2222 = show1: SMALL cards, show2: BIG cards
    # 3333 = both normal random
    "last_commands": set()  # Track used commands for single reply
}

# Teen Patti Ranks
RANK_ORDER = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
suits = ["♦️", "♣️", "♥️", "♠️"]
deck = [(r, s) for s in suits for r in RANK_ORDER.keys()]

# Indian Teen Patti Ranks (highest to weakest)
TEEN_PATTI_RANKS = {
    "trails": 0,           # 3 same cards (highest)
    "pure_sequence": 1,    # Same suit sequence
    "colour": 2,           # Same suit (non-sequence)
    "pair": 3,             # 2 same cards
    "sequence": 4,         # Different suit sequence
    "high_card": 5         # No combination
}

def get_card_strength(card):
    return RANK_ORDER[card[0]]

def evaluate_hand(cards):
    """Evaluate Indian Teen Patti hand"""
    ranks = [get_card_strength(c[0]) for c in cards]
    suits_list = [c[1] for c in cards]
    ranks_sorted = sorted(ranks)
    
    # Check trails (3 same)
    if ranks_sorted[0] == ranks_sorted[2]:
        return ("trails", ranks_sorted[0] * 100)
    
    # Check pure sequence
    is_same_suit = len(set(suits_list)) == 1
    is_sequence = (ranks_sorted[2] - ranks_sorted[0] == 2) and (ranks_sorted[1] - ranks_sorted[0] == 1)
    
    if is_same_suit and is_sequence:
        return ("pure_sequence", ranks_sorted[2] * 100)
    
    # Check colour
    if is_same_suit:
        return ("colour", sum(ranks) * 10)
    
    # Check pair
    for i in range(len(ranks)):
        for j in range(i+1, len(ranks)):
            if ranks[i] == ranks[j]:
                return ("pair", ranks[i] * 100)
    
    # Check sequence
    if is_sequence:
        return ("sequence", ranks_sorted[2] * 100)
    
    return ("high_card", sum(ranks))

def generate_trails():
    rank = random.choice(list(RANK_ORDER.keys()))
    selected_suits = random.sample(suits, 3)
    return [(rank, s) for s in selected_suits]

def generate_pure_sequence():
    suit = random.choice(suits)
    start_rank = random.choice(list(RANK_ORDER.keys())[:-2])
    start_val = RANK_ORDER[start_rank]
    sequence_ranks = [str(start_val + i) if start_val + i <= 10 else 
                      ["J", "Q", "K", "A"][start_val + i - 11] for i in range(3)]
    return [(r, suit) for r in sequence_ranks]

def generate_colour():
    suit = random.choice(suits)
    ranks = random.sample(list(RANK_ORDER.keys()), 3)
    return [(r, suit) for r in ranks]

def generate_pair():
    pair_rank = random.choice(list(RANK_ORDER.keys()))
    pair_suits = random.sample(suits, 2)
    third_rank = random.choice([r for r in RANK_ORDER.keys() if r != pair_rank])
    third_suit = random.choice(suits)
    return [(pair_rank, s) for s in pair_suits] + [(third_rank, third_suit)]

def generate_sequence():
    start_rank = random.choice(list(RANK_ORDER.keys())[:-2])
    start_val = RANK_ORDER[start_rank]
    sequence_ranks = [str(start_val + i) if start_val + i <= 10 else 
                      ["J", "Q", "K", "A"][start_val + i - 11] for i in range(3)]
    selected_suits = random.sample(suits, 3)
    return [(r, s) for r, s in zip(sequence_ranks, selected_suits)]

def generate_big_cards():
    """BIG cards - combinations preferred"""
    combination = random.choice(["trails", "pure_sequence", "colour", "pair", "sequence"])
    
    if combination == "trails":
        return generate_trails()
    elif combination == "pure_sequence":
        return generate_pure_sequence()
    elif combination == "colour":
        return generate_colour()
    elif combination == "pair":
        return generate_pair()
    elif combination == "sequence":
        return generate_sequence()
    
    high_subset = [c for c in deck if RANK_ORDER[c[0]] >= 10]
    return random.sample(high_subset, 3)

def generate_small_cards():
    """SMALL cards - low rank random"""
    small_subset = [c for c in deck if RANK_ORDER[c[0]] <= 7]
    return random.sample(small_subset, 3)

def generate_random_cards():
    """Completely random"""
    return random.sample(deck, 3)

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
    except: 
        await context.bot.leave_chat(chat_id)
        return False

async def anti_promotion_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block promotional messages from non-admins"""
    user = update.effective_user
    try:
        user_stat = await context.bot.get_chat_member(update.effective_chat.id, user.id)
        if user_stat.status in ["administrator", "creator"]:
            return True
        
        promotion_keywords = ["buy", "join", "subscribe", "promotion", "ads", "discount", 
                             "offer", "click here", "link", "website", "casino", "betting"]
        message_text = update.message.text.lower() if update.message.text else ""
        
        for keyword in promotion_keywords:
            if keyword in message_text:
                await update.message.reply_text("❌ Promotion not allowed!")
                await update.message.delete()
                return False
        return True
    except:
        return True

# --- COMMANDS ---
async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    
    # ERROR if /show alone (no argument)
    if len(context.args) == 0:
        await update.message.reply_text("❌ Error: /show ke aage 1 ya 2 likho. Example: /show 1 ya /show 2")
        return
    
    cmd_arg = context.args[0].lower()
    if cmd_arg not in ["1", "2"]:
        await update.message.reply_text("❌ Error: Sirf /show 1 ya /show 2 use karein")
        return
    
    # Single reply tracking
    command_key = f"show_{cmd_arg}"
    if command_key in bot_state["last_commands"]:
        await update.message.reply_text("⚠️ Already used this command recently")
        return
    bot_state["last_commands"].add(command_key)
    
    special_mode = bot_state["special_mode"]
    show_mode = cmd_arg
    
    cards = None
    
    if special_mode == "1111":
        # show 1 = BIG, show 2 = SMALL
        if show_mode == "1":
            cards = generate_big_cards()
        else:
            cards = generate_small_cards()
    elif special_mode == "2222":
        # show 1 = SMALL, show 2 = BIG
        if show_mode == "1":
            cards = generate_small_cards()
        else:
            cards = generate_big_cards()
    else:  # 3333
        cards = generate_random_cards()
    
    res = "
".join([f"{c[0]} {c[1]}" for c in cards])
    hand_eval = evaluate_hand(cards)
    await update.message.reply_text(f"Cards Result:
{res}

Hand: {hand_eval[0]}")

async def roll_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    
    # Single reply tracking
    if "roll" in bot_state["last_commands"]:
        await update.message.reply_text("⚠️ Already used /roll recently")
        return
    bot_state["last_commands"].add("roll")
    
    cmd = update.message.text.lower()
    if "rol" in cmd and "rolll" not in cmd: 
        res = random.choice([2, 4, 6])
    elif "rolll" in cmd: 
        res = random.choice([1, 3, 5])
    else: 
        res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    
    # Single reply tracking
    if "sps" in bot_state["last_commands"]:
        await update.message.reply_text("⚠️ Already used /sps recently")
        return
    bot_state["last_commands"].add("sps")
    
    await update.message.reply_text(random.choice(["Stone", "Paper", "Scissors"]))

async def set_special_mode_1111(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    
    bot_state["special_mode"] = "1111"
    bot_state["last_commands"].clear()
    await update.message.reply_text("✅ Mode 1111 Active: /show 1 = BIG Cards, /show 2 = SMALL Cards")

async def set_special_mode_2222(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    
    bot_state["special_mode"] = "2222"
    bot_state["last_commands"].clear()
    await update.message.reply_text("✅ Mode 2222 Active: /show 1 = SMALL Cards, /show 2 = BIG Cards")

async def set_special_mode_3333(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await security_check(update, context): return
    
    bot_state["special_mode"] = "3333"
    bot_state["last_commands"].clear()
    await update.message.reply_text("✅ Mode 3333 Active: Normal Random Cards")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("show", show_result))
    application.add_handler(CommandHandler(["roll", "rol", "rolll"], roll_logic))
    application.add_handler(CommandHandler("sps", sps))
    application.add_handler(CommandHandler("1111", set_special_mode_1111))
    application.add_handler(CommandHandler("2222", set_special_mode_2222))
    application.add_handler(CommandHandler("3333", set_special_mode_3333))
    
    application.run_polling()
