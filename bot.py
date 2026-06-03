import telebot,
from flask import Flask
from threading import Thread

# Flask server taaki Render bot ko band na kare
app = Flask('')
@app.route('/')
def home(): return "Teen Patti Bot is Active!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()

# Bot Setup
API_TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# Teen Patti Cards logic
suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def get_card():
    return f"{random.choice(ranks)}{random.choice(suits)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Teen Patti Bot Ready! /card ya /roll use karein.")

@bot.message_handler(commands=['card'])
def handle_card(message):
    # Teen Patti ke liye 3 cards
    cards = [get_card() for _ in range(3)]
    bot.reply_to(message, f"Aapke cards: {' '.join(cards)}")

@bot.message_handler(commands=['roll'])
def handle_roll(message):
    # Sirf 1, 3, 5 ka logic
    bot.reply_to(message, str(random.choice([1, 3, 5])))

if __name__ == "__main__":
    bot.infinity_polling(none_stop=True)
