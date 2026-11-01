import logging
import os
from flask import Flask
import telebot
from telebot import types

# إعدادات التسجيل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# إعدادات البوت والتوكن
TOKEN = "8768205999:AAFScqbBy0iV18bOi3DSv7yOrGi-fl1vMJU"
ADMIN_ID = 7192769549

# إعداد سيرفر خفيف لضمان استمرار البوت 24/7 على Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7 successfully!"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('📚 الأرشيف والمحاضرات')
    item2 = types.KeyboardButton('ℹ️ معلومات عنا')
    markup.add(item1, item2)
    
    bot.reply_to(message, "مرحباً بك يا مهندس في بوت أرشيف هندسة جامعة الخرطوم! 🎓\nاختر من الأزرار أدناه:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == '📚 الأرشيف والمحاضرات':
        semesters_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.reply_to(message, "قريباً سيتم توفير روابط المحاضرات والمواد هنا.", reply_markup=semesters_markup)
    elif message.text == 'ℹ️ معلومات عنا':
        bot.reply_to(message, "هذا البوت مخصص لمساعدة طلاب كلية الدراسات التقنية والتنموية - جامعة الخرطوم.")
    else:
        bot.reply_to(message, "عجباً، لم أفهم هذا الأمر. استخدم القائمة الرئيسية.")

if __name__ == "__main__":
    import threading
    # تشغيل سيرفر الـ Flask في الخلفية
    def run_flask():
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
    t = threading.Thread(target=run_flask)
    t.start()
    
    # تشغيل بوت التليجرام
    print("Bot is polling...")
    bot.infinity_polling()
