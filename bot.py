import os
from flask import Flask
import telebot
from telebot import types
import threading

TOKEN = "8768205999:AAFvG3jFRDIm6n8gnb9sBdZgBFNgEqqWOsA"
ADMIN_ID = 7192769549

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
    if message.text == '📚 الأرشيف والمحاضرات' or message.text == 'القائمة الرئيسية':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('هندسة التحكم الكهربائي')
        item2 = types.KeyboardButton('القائمة الرئيسية')
        markup.add(item1, item2)
        bot.reply_to(message, "اختر التخصص المطلوب:", reply_markup=markup)
        
    elif message.text == 'هندسة التحكم الكهربائي':
        sem_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        sem1 = types.KeyboardButton('السمستر الأول')
        sem2 = types.KeyboardButton('السمستر الثاني')
        back_main = types.KeyboardButton('📚 الأرشيف والمحاضرات')
        sem_markup.add(sem1, sem2)
        sem_markup.add(back_main)
        bot.reply_to(message, "اختر السمستر المطلوب:", reply_markup=sem_markup)
        
    elif message.text == 'السمستر الأول' or message.text == 'السمستر الثاني':
        sub_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        sub1 = types.KeyboardButton('الدوائر الكهربائية (EEG125)')
        back_sem = types.KeyboardButton('هندسة التحكم الكهربائي')
        sub_markup.add(sub1)
        sub_markup.add(back_sem)
        bot.reply_to(message, f"أنت الآن في {message.text}. اختر المادة الدراسية:", reply_markup=sub_markup)

    elif message.text == 'الدوائر الكهربائية (EEG125)':
        type_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        t1 = types.KeyboardButton('شيتات')
        t2 = types.KeyboardButton('محاضرات')
        t3 = types.KeyboardButton('امتحانات سابقة')
        back_mat = types.KeyboardButton('السمستر الأول')
        type_markup.add(t1, t2, t3)
        type_markup.add(back_mat)
        bot.reply_to(message, "اختر نوع المحتوى المطلوب للمادة:", reply_markup=type_markup)

    elif message.text == 'شيتات':
        bot.reply_to(message, "هنا سيتم رفع وعرض الشيتات الخاصة بالمادة.")
    elif message.text == 'محاضرات':
        bot.reply_to(message, "هنا سيتم رفع وعرض المحاضرات الخاصة بالمادة.")
    elif message.text == 'امتحانات سابقة':
        bot.reply_to(message, "هنا سيتم رفع وعرض الامتحانات السابقة للمادة.")

    elif message.text == 'ℹ️ معلومات عنا':
        bot.reply_to(message, f"هذا البوت مخصص لمساعدة طلاب كلية الدراسات التقنية والتنموية - جامعة الخرطوم.\nمعرف المشرف: {ADMIN_ID}")
    else:
        bot.reply_to(message, "عجباً، لم أفهم هذا الأمر. استخدم الأزرار الظاهرة في القائمة.")

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

t = threading.Thread(target=run_flask)
t.start()

print("Bot is polling...")
bot.infinity_polling()
