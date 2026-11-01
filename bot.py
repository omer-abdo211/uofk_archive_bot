import os
import threading

import telebot
from flask import Flask
from telebot import types

# ===== الإعدادات =====
# ضع التوكن في Render: Environment -> BOT_TOKEN
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7192769549"))

if not TOKEN:
    raise SystemExit("BOT_TOKEN غير موجود. أضفه في Environment Variables في Render.")

bot = telebot.TeleBot(TOKEN)
app = Flask("uofk_bot")


@app.route("/")
def home():
    return "Bot is running 24/7 successfully!"


# ===== البيانات =====
MAJORS = [
    "هندسة التحكم الكهربائي",
    "هندسة القدرة الكهربائية",
    "هندسة الطبية",
    "هندسة الشبكات",
]

SEM1 = "المستوى الأول - السمستر الأول"
SEM2 = "المستوى الأول - السمستر الثاني"

SUBJECTS = {
    SEM1: [
        "لغة إنجليزية 1 (EE 111)",
        "الحسبان (EE 112)",
        "الفيزياء (EE 113)",
        "مقدمة الحاسوب (EE 114)",
        "أعمال الورش 1 (EE 115)",
        "رسم هندسي (EE 116)",
    ],
    SEM2: [
        "لغة إنجليزية 2 (EE 121)",
        "أخلاقيات المهنة (EE 122)",
        "الجبر الخطى والمعادلات التفاضلية (EE 123)",
        "برمجة الحاسوب (EE 124)",
        "أساسيات الهندسة الكهربائية (EE 125)",
        "أساسيات الالكترونيات التماثلية (EE 126)",
        "ميكانيكا الهندسة (ديناميكا واستاتيكا) (EE 127)",
    ],
}

ALL_SUBJECTS = [s for subs in SUBJECTS.values() for s in subs]
CONTENT_TYPES = ["شيتات", "محاضرات", "امتحانات سابقة"]
MAIN_MENU = "القائمة الرئيسية"
ABOUT = "ℹ️ معلومات عنا"


# ===== القوائم =====
def main_markup():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(MAJORS[0], MAJORS[1])
    m.add(MAJORS[2], MAJORS[3])
    m.add(ABOUT)
    return m


def semester_markup():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(SEM1, SEM2)
    m.add(MAIN_MENU)
    return m


def subjects_markup(semester):
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subject in SUBJECTS[semester]:
        m.add(subject)
    m.add(MAIN_MENU)
    return m


def content_markup():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(*CONTENT_TYPES)
    m.add(MAIN_MENU)
    return m


# ===== الأوامر =====
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "مرحباً بك يا مهندس في بوت أرشيف هندسة جامعة الخرطوم! 🎓\nاختر التخصص المطلوب:",
        reply_markup=main_markup(),
    )


@bot.message_handler(func=lambda message: True)
def handle_all(message):
    text = (message.text or "").strip()

    if text in MAJORS:
        bot.reply_to(
            message,
            f"أنت اخترت تخصص: {text}\nاختر السمستر المطلوب:",
            reply_markup=semester_markup(),
        )

    elif text in SUBJECTS:
        bot.reply_to(
            message,
            f"{text}: اختر المادة:",
            reply_markup=subjects_markup(text),
        )

    elif text in ALL_SUBJECTS:
        bot.reply_to(
            message,
            f"أنت اخترت مادة: {text}\nاختر نوع المحتوى المطلوب:",
            reply_markup=content_markup(),
        )

    elif text in CONTENT_TYPES:
        bot.reply_to(message, f"هنا سيتم رفع وعرض المحتوى ({text}) الخاص بالمادة قريباً.")

    elif text == MAIN_MENU:
        bot.reply_to(
            message,
            "تم العودة للقائمة الرئيسية. اختر التخصص المطلوب:",
            reply_markup=main_markup(),
        )

    elif text == ABOUT:
        bot.reply_to(
            message,
            "هذا البوت مخصص لمساعدة طلاب كلية الدراسات التقنية والتنموية - جامعة الخرطوم.\n"
            f"معرف المشرف: {ADMIN_ID}",
        )

    else:
        bot.reply_to(message, "لم أفهم هذا الأمر. استخدم الأزرار الظاهرة في القائمة.")


# ===== التشغيل =====
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


threading.Thread(target=run_flask, daemon=True).start()
bot.remove_webhook()
print("Bot is polling...")
bot.infinity_polling(skip_pending=True)
