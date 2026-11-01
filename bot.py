import logging
import os
from flask import Flask
from threading import Thread
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# تفعيل تسجيل الأخطاء
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- الإعدادات الأساسية (نفس التوكن الثابت بدون تغيير) ---
TOKEN = "8768205999:AAFW7kHxgSZYuFeA0gpZkK1LsL1AItqORRU"
ADMIN_ID = 7192709549  # رقمك الخاص لصلاحيات الرفع الحصرية

# --- إعداد سيرفر خفيف لضمان استمرار البوت 24/7 على Render ---
app = Flask('')

@app.route('/')
def home():
    return "UofK Archive Bot is active and running 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- قاعدة بيانات أرقام الملفات (File IDs) لمستودع الأرشيف ---
ARCHIVE_DATABASE = {
    "control_sem1_sheets": "ضع_هنا_File_ID_الشيتات",
    "control_sem1_lectures": "ضع_هنا_File_ID_المحاضرات",
    "control_sem1_exams": "ضع_هنا_File_ID_الامتحانات",
}

# --- تعريف الأزرار والقوائم (Reply Keyboards) ---
main_menu_keyboard = [
    ["الهندسة الكهربائية (تحكم)", "الهندسة الكهربائية (قدرة)"],
    ["هندسة طبية", "هندسة شبكات"],
    ["التعريف بالبوت"],
]
main_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

semesters_keyboard = [
    ["المستوى الأول", "المستوى الثاني"],
    ["الرجوع للتخصصات"],
]
semesters_markup = ReplyKeyboardMarkup(semesters_keyboard, resize_keyboard=True)

# مواد المستوى الأول المشتركة والتخصصية الدقيقة
sem1_subjects_keyboard = [
    ["لغة إنجليزية 1", "الحسبان"],
    ["الفيزياء", "مقدمة الحاسوب"],
    ["أعمال الورش 1", "رسم هندسي"],
    ["ميكانيكا الهندسة (ديناميكا واستاتيكا)"],
    ["الكيمياء العامة", "أساسيات تصميم النظم الرقمية"],
    ["الرجوع للمستويات"],
]
sem1_subjects_markup = ReplyKeyboardMarkup(sem1_subjects_keyboard, resize_keyboard=True)

# مواد المستوى الثاني المشتركة والتخصصية
sem2_subjects_keyboard = [
    ["لغة إنجليزية 2", "أخلاقيات المهنة"],
    ["الجبر الخطي والمعادلات التفاضلية", "برمجة الحاسوب"],
    ["أساسيات الهندسة الكهربائية", "أساسيات الالكترونيات التمثالية"],
    ["الرجوع للمستويات"],
]
sem2_subjects_markup = ReplyKeyboardMarkup(sem2_subjects_keyboard, resize_keyboard=True)

sections_keyboard = [
    ["شيتات", "محاضرات", "امتحانات سابقة"],
    ["الرجوع للمواد"],
]
sections_markup = ReplyKeyboardMarkup(sections_keyboard, resize_keyboard=True)


# --- دوال البوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"أهلاً بك يا مهندس {user.first_name} في الأرشيف المركزي لكلية الهندسة - جامعة الخرطوم.\nاختر التخصص المناسب من لوحة المفاتيح بالأسفل:",
        reply_markup=main_markup,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    chat_data = context.user_data

    if text in ["الهندسة الكهربائية (تحكم)", "الهندسة الكهربائية (قدرة)", "هندسة طبية", "هندسة شبكات"]:
        chat_data["current_specialty"] = text
        await update.message.reply_text(
            f"تم اختيار تخصص: {text}\nاختر المستوى الدراسي:",
            reply_markup=semesters_markup,
        )

    elif text == "المستوى الأول":
        chat_data["current_sem"] = "sem1"
        await update.message.reply_text(
            "اختر مادة المستوى الأول:", reply_markup=sem1_subjects_markup
        )

    elif text == "المستوى الثاني":
        chat_data["current_sem"] = "sem2"
        await update.message.reply_text(
            "اختر مادة المستوى الثاني:", reply_markup=sem2_subjects_markup
        )

    elif text in [
        "لغة إنجليزية 1", "الحسبان", "الفيزياء", "مقدمة الحاسوب", "أعمال الورش 1", "رسم هندسي",
        "ميكانيكا الهندسة (ديناميكا واستاتيكا)", "الكيمياء العامة", "أساسيات تصميم النظم الرقمية",
        "لغة إنجليزية 2", "أخلاقيات المهنة", "الجبر الخطي والمعادلات التفاضلية", 
        "برمجة الحاسوب", "أساسيات الهندسة الكهربائية", "أساسيات الالكترونيات التمثالية"
    ]:
        chat_data["current_subject"] = text
        await update.message.reply_text(
            f"مادة: {text}\nاختر القسم المطلوب للملفات:",
            reply_markup=sections_markup,
        )

    elif text in ["شيتات", "محاضرات", "امتحانات سابقة"]:
        subject = chat_data.get("current_subject", "المادة")
        file_id = ARCHIVE_DATABASE.get("control_sem1_sheets")

        if file_id and not file_id.startswith("ضع_هنا"):
            try:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=file_id,
                    caption=f"أرشيف كلية الهندسة - {subject} ({text})",
                )
            except Exception:
                await update.message.reply_text("عذراً، حدث خطأ أثناء إرسال الملف من المستودع.")
        else:
            await update.message.reply_text(
                f"📁 قسم ({text}) لم يتم ربط ملفاته بمادة ({subject}) بعد من قبل المشرف."
            )

    elif text in ["التعريف بالبوت"]:
        await update.message.reply_text(
            "هذا البوت مخصص لأرشفة وتوفير المواد الدراسية والشيتات لطلاب كلية الدراسات التقنية والتنموية - جامعة الخرطوم.",
            reply_markup=main_markup,
        )

    elif text in ["الرجوع للتخصصات"]:
        await update.message.reply_text(
            "القائمة الرئيسية - اختر التخصص:", reply_markup=main_markup
        )

    elif text == "الرجوع للمستويات":
        await update.message.reply_text(
            "اختر المستوى الدراسي:", reply_markup=semesters_markup
        )

    elif text == "الرجوع للمواد":
        sem = chat_data.get("current_sem")
        markup = sem1_subjects_markup if sem == "sem1" else sem2_subjects_markup
        await update.message.reply_text("اختر المادة:", reply_markup=markup)

    else:
        if user_id == ADMIN_ID:
            if update.message.document:
                file_id = update.message.document.file_id
                file_name = update.message.document.file_name
                await update.message.reply_text(
                    f"✅ تم استلام الملف بنجاح في المستودع الحصري!\nاسم الملف: {file_name}\n\nFile ID الخاص به للاستخدام:\n`{file_id}`",
                    parse_mode="Markdown",
                )
            else:
                await update.message.reply_text(
                    "أهلاً بك يا مهندس في وضع المشرف. أرسل أي ملف لاستخراج الـ File ID الخاص به."
                )
        else:
            await update.message.reply_text(
                "يرجى استخدام الأزرار الظاهرة أسفل الشاشة للتنقل بشكل صحيح."
            )


def main():
    # تشغيل سيرفر الـ Keep-alive في الخلفية لضمان عمل البوت 24/7 على Render
    keep_alive()

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_message))

    print("البوت يعمل الآن بدون تكرار وبثبات تام 24/7...")
    app.run_polling()


if __name__ == "__main__":
    main()
