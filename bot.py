import os
from flask import Flask
import telebot
from telebot import types
import threading

TOKEN = "8768205999:AAGxMr6XFw3lkKHEWUuZkrFTrSbKChb4aH0"
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
        item2 = types.KeyboardButton('هندسة القدرة الكهربائية')
        item3 = types.KeyboardButton('هندسة الطبية')
        item4 = types.KeyboardButton('هندسة الشبكات')
        back_main = types.KeyboardButton('ℹ️ معلومات عنا')
        markup.add(item1, item2)
        markup.add(item3, item4)
        markup.add(back_main)
        bot.reply_to(message, "اختر التخصص المطلوب:", reply_markup=markup)
        
    elif message.text in ['هندسة التحكم الكهربائي', 'هندسة القدرة الكهربائية', 'هندسة الطبية', 'هندسة الشبكات']:
        sem_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        sem1 = types.KeyboardButton('المستوى الأول - السمستر الأول')
        sem2 = types.KeyboardButton('المستوى الأول - السمستر الثاني')
        back_main = types.KeyboardButton('📚 الأرشيف والمحاضرات')
        sem_markup.add(sem1, sem2)
        sem_markup.add(back_main)
        bot.reply_to(message, f"أنت اخترت تخصص: {message.text}\nاختر السمستر المطلوب:", reply_markup=sem_markup)
        
    elif message.text == 'المستوى الأول - السمستر الأول':
        sub_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        sub_markup.add(types.KeyboardButton('لغة إنجليزية 1 (EE 111)'))
        sub_markup.add(types.KeyboardButton('الحسبان (EE 112)'))
        sub_markup.add(types.KeyboardButton('الفيزياء (EE 113)'))
        sub_markup.add(types.KeyboardButton('مقدمة الحاسوب (EE 114)'))
        sub_markup.add(types.KeyboardButton('أعمال الورش 1 (EE 115)'))
        sub_markup.add(types.KeyboardButton('رسم هندسي (EE 116)'))
        sub_markup.add(types.KeyboardButton('هندسة التحكم الكهربائي'))
        bot.reply_to(message, "مقررات المستوى الأول - السمستر الأول: اختر المادة:", reply_markup=sub_markup)

    elif message.text == 'المستوى الأول - السمستر الثاني':
        sub_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        sub_markup.add(types.KeyboardButton('لغة إنجليزية 2 (EE 121)'))
        sub_markup.add(types.KeyboardButton('أخلاقيات المهنة (EE 122)'))
        sub_markup.add(types.KeyboardButton('الجبر الخطى والمعادلات التفاضلية (EE 123)'))
        sub_markup.add(types.KeyboardButton('برمجة الحاسوب (EE 124)'))
        sub_markup.add(types.KeyboardButton('أساسيات الهندسة الكهربائية (EE 125)'))
        sub_markup.add(types.KeyboardButton('أساسيات الالكترونيات التماثلية (EE 126)'))
        sub_markup.add(types.KeyboardButton('ميكانيكا الهندسة (ديناميكا واستاتيكا) (EE 127)'))
        sub_markup.add(types.KeyboardButton('هندسة التحكم الكهربائي'))
        bot.reply_to(message, "مقررات المستوى الأول - السمستر الثاني: اختر المادة:", reply_markup=sub_markup)

    elif message.text in [
        'لغة إنجليزية 1 (EE 111)', 'الحسبان (EE 112)', 'الفيزياء (EE 113)', 
        'مقدمة الحاسوب (EE 114)', 'أعمال الورش 1 (EE 115)', 'رسم هندسي (EE 116)', 
        'لغة إنجليزية 2 (EE 121)', 'أخلاقيات المهنة (EE 122)', 'الجبر الخطى والمعادلات التفاضلية (EE 123)',
        'برمجة الحاسوب (EE 124)', 'أساسيات الهندسة الكهربائية (EE 125)', 
        'أساسيات الالكترونيات التماثلية (EE 126)', 'ميكانيكا الهندسة (ديناميكا واستاتيكا) (EE 127)'
    ]:
        type_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        t1 = types.KeyboardButton('شيتات')
        t2 = types.KeyboardButton('محاضرات')
        t3 = types.KeyboardButton('امتحانات سابقة')
        back_mat = types.KeyboardButton('المستوى الأول - السمستر الثاني')
        type_markup.add(t1, t2, t3)
        type_markup.add(back_mat)
        bot.reply_to(message, f"أنت اخترت مادة: {message.text}\nاختر نوع المحتوى المطلوب:", reply_markup=type_markup)

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
