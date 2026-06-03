import random
import threading
import time
import requests

from flask import Flask
from telegram import Update
from telegram.ext import (
ApplicationBuilder,
CommandHandler,
ContextTypes
)

==========================

CONFIG

==========================

TOKEN = "YOUR_NEW_BOT_TOKEN"
OWNER_ID = 7007926290

Render URL

RENDER_URL = "https://your-app-name.onrender.com"

==========================

FLASK SERVER

==========================

app = Flask(name)

@app.route("/")
def home():
return "Bot is Alive!"

def run_flask():
app.run(host="0.0.0.0", port=8080)

==========================

KEEP ALIVE

==========================

def keep_alive():
while True:
try:
requests.get(RENDER_URL, timeout=10)
print("Keep Alive Ping Sent")
except Exception as e:
print(e)

time.sleep(300)  # 5 min

==========================

AUTHORIZATION

==========================

async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):

chat_id = update.effective_chat.id  
user_id = update.effective_user.id  

try:  
    owner_member = await context.bot.get_chat_member(  
        chat_id,  
        OWNER_ID  
    )  

    # Owner admin nahi hai  
    if owner_member.status not in [  
        "creator",  
        "administrator"  
    ]:  
        await context.bot.leave_chat(chat_id)  
        return False  

except:  
    await context.bot.leave_chat(chat_id)  
    return False  

member = await context.bot.get_chat_member(  
    chat_id,  
    user_id  
)  

# Sirf admin use kar sakta hai  
if member.status not in [  
    "creator",  
    "administrator"  
]:  
    return False  

return True

==========================

SHOW COMMAND

==========================

async def show(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not await is_authorized(update, context):
    return

# /show likhne par error
if not context.args:
    await update.message.reply_text(
        "❌ Enter value\nExample: /show 1"
    )
    return

value = context.args[0]

suits = ["♥️", "♦️", "♠️", "♣️"]
ranks = [
    "2","3","4","5","6","7",
    "8","9","10","J","Q","K","A"
]

# 3 alag replies
for _ in range(3):

    card = f"{random.choice(suits)}{random.choice(ranks)}"

    await update.message.reply_text(
        f"/show {value}\n\n{value} cards: {card}"
    )

==========================

SPS COMMAND

==========================

async def sps(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not await is_authorized(update, context):  
    return  

result = random.choice([  
    "Stone",  
    "Paper",  
    "Scissors"  
])  

await update.message.reply_text(  
    f"SPS: {result}"  
)

==========================

ROLL COMMAND

==========================

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):

if not await is_authorized(update, context):  
    return  

await update.message.reply_text(  
    str(random.randint(1, 6))  
)

==========================

MAIN

==========================

if name == "main":

threading.Thread(  
    target=run_flask,  
    daemon=True  
).start()  

threading.Thread(  
    target=keep_alive,  
    daemon=True  
).start()  

app_bot = (  
    ApplicationBuilder()  
    .token(TOKEN)  
    .build()  
)  

app_bot.add_handler(  
    CommandHandler("show", show)  
)  

app_bot.add_handler(  
    CommandHandler("sps", sps)  
)  

app_bot.add_handler(  
    CommandHandler("roll", roll)  
)  

print("Bot Started...")  

app_bot.run_polling(  
    drop_pending_updates=True  
)

Karo iske sahi woh jo abhi bataya tumko mene
