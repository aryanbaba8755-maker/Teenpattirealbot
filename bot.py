import random
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8699525997:AAEkJ7ePN7RjCTvonA_WGtExPl46D8gDdM4"
OWNER_ID = 7007926290

# Bot ka State
bot_state = {"roll_mode": "normal", "show_mode": "none"}

# --- Security & Safety Check ---
async def safety_check(update, context):
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. Owner presence check (Agar owner nahi hai, bot leave kar dega)
    try:
        await context.bot.get_chat_member(chat.id, OWNER_ID)
    except:
        await context.bot.leave_chat(chat.id)
        return False
        
    # 2. Permission check (Owner ya Admin)
    if user.id == OWNER_ID: return True
    member = await context.bot.get_chat_member(chat.id, user.id)
    return member.status in ['administrator', 'creator']

# --- Game Logic ---
async def roll(update, context):
    if not await safety_check(update, context): return
    mode = bot_state["roll_mode"]
    
    if mode == "odd": res = random.choice([1, 3, 5])
    elif mode == "even": res = random.choice([2, 4, 6])
    elif mode == "even_heavy": res = random.choices([1,2,3,4,5,6], weights=[10, 25, 10, 25, 10, 20])[0]
    else: res = random.randint(1, 6)
    await update.message.reply_text(str(res))

async def show(update, context):
    if not await safety_check(update, context): return
    args = context.args
    if not args or args[0] not in ["1", "2"]:
        await update.message.reply_text("❌ Command Error! Use: /show 1 or /show 2")
        return
    
    val = args[0]
    mode = bot_state["show_mode"]
    
    # Win Logic (Show 1/Show 2 badlaav)
    if mode == "win1": pool = ["J", "Q", "K", "A"] if val == "1" else ["2", "3", "4"]
    elif mode == "win2": pool = ["2", "3", "4"] if val == "1" else ["J", "Q", "K", "A"]
    else: pool = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
    
    for _ in range(3):
        card = f"{val} cards {random.choice(pool)}{random.choice(['♦️','♣️','♥️','♠️'])}"
        await update.message.reply_text(card)

async def set_mode(update, context):
    if not await safety_check(update, context): return
    cmd = update.message.text
    if "/11" in cmd: bot_state["roll_mode"] = "odd"
    elif "/22" in cmd: bot_state["roll_mode"] = "even"
    elif "/33" in cmd: bot_state["roll_mode"] = "normal"
    elif "/21" in cmd: bot_state["roll_mode"] = "even_heavy"
    elif "/win11" in cmd: bot_state["show_mode"] = "win1"
    elif "/win22" in cmd: bot_state["show_mode"] = "win2"
    await update.message.reply_text(f"✅ Mode set to: {cmd}")

# --- Bot Start ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("show", show))
    app.add_handler(CommandHandler(["11", "22", "33", "21", "win11", "win22"], set_mode))
    app.add_handler(CommandHandler("sps", lambda u, c: u.message.reply_text(random.choice(["Stone", "Paper", "Scissors"])) if True else None))
    
    print("Bot is ready and secure.")
    app.run_polling(drop_pending_updates=True)
