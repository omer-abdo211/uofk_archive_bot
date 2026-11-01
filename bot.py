import os
from flask import Flask
import telebot
from telebot import types

TOKEN = "876820599:AAFW7KhxgSZYuFeA6pZkK1LsL1Ai tQORRU"

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
    if message.text == '📚 الأرشيف والمحاضرات' or message.text == 'الرجوع للمواد':
        semesters_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_s1 = types.KeyboardButton('شيتات')
        item_s2 = types.KeyboardButton('محاضرات')
        item_s3 = types.KeyboardButton('امتحانات سابقة')
        semesters_markup.add(item_s1, item_s2, item_s3)
        bot.reply_to(message, "اختر القسم المطلوب من الأرشيف:", reply_markup=semesters_markup)
    elif message.text == 'شيتات':
        bot.reply_to(message, "هنا سيتم عرض الشيتات الخاصة بالمواد.")
    elif message.text == 'محاضرات':
        bot.reply_to(message, "هنا سيتم عرض المحاضرات.")
    elif message.text == 'امتحانات سابقة':
        bot.reply_to(message, "هنا سيتم عرض الامتحانات السابقة.")
    elif message.text == 'ℹ️ معلومات عنا':
        bot.reply_to(message, "هذا البوت مخصص لمساعدة طلاب كلية الدراسات التقنية والتنموية - جامعة الخرطوم.")
    else:
        bot.reply_to(message, "عجباً، لم أفهم هذا الأمر. استخدم القائمة الرئيسية.")

if name == "main":
    import threading
    def run_flask():
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
    t = threading.Thread(target=run_flask)
    t.start()
    
    print("Bot is polling...")
    bot.infinity_polling()
