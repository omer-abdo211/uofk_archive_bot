import os
from flask import Flask
import telebot
from telebot import types
import threading

TOKEN = "8768205999:AAEDK2HvyI4JDI8eg8Lg-w0zhGgPx5EiPtY"
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
    if message.text == '📚 الأرشيف والمحاضرات' or message.text == 'الرجوع للمواد':
        semesters_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_s1 = types.KeyboardButton('السمستر الأول')
        item_s2 = types.KeyboardButton('السمستر الثاني')
        item_back = types.KeyboardButton('القائمة الرئيسية')
        semesters_markup.add(item_s1, item_s2)
        semesters_markup.add(item_back)
        bot.reply_to(message, "اختر السمستر أو القسم المطلوب من الأرشيف:", reply_markup=semesters_markup)
        
    elif message.text == 'السمستر الأول':
        sub_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        sub_1 = types.KeyboardButton('شيتات')
        sub_2 = types.KeyboardButton('محاضرات')
        sub_3 = types.KeyboardButton('امتحانات سابقة')
        back_btn = types.KeyboardButton('الرجوع للمواد')
        sub_markup.add(sub_1, sub_2, sub_3)
        sub_markup.add(back_btn)
        bot.reply_to(message, "أنت الآن في السمستر الأول. اختر المحتوى المطلوب:", reply_markup=sub_markup)

    elif message.text == 'السمستر الثاني':
        sub_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        sub_1 = types.KeyboardButton('شيتات')
        sub_2 = types.KeyboardButton('محاضرات')
        sub_3 = types.KeyboardButton('امتحانات سابقة')
        back_btn = types.KeyboardButton('الرجوع للمواد')
        sub_markup.add(sub_1, sub_2, sub_3)
        sub_markup.add(back_btn)
        bot.reply_to(message, "أنت الآن في السمستر الثاني. اختر المحتوى المطلوب:", reply_markup=sub_markup)

    elif message.text == 'شيتات':
        bot.reply_to(message, "هنا سيتم عرض الشيتات الخاصة بالمواد والأرشيف الداخلي للقناة.")
    elif message.text == 'محاضرات':
        bot.reply_to(message, "هنا سيتم عرض المحاضرات والروابط الخاصة بها.")
    elif message.text == 'امتحانات سابقة':
        bot.reply_to(message, "هنا سيتم عرض الأوراق والامتحانات السابقة.")
        
    elif message.text == 'القائمة الرئيسية':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('📚 الأرشيف والمحاضرات')
        item2 = types.KeyboardButton('ℹ️ معلومات عنا')
        markup.add(item1, item2)
        bot.reply_to(message, "تم العودة للقائمة الرئيسية:", reply_markup=markup)
        
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
