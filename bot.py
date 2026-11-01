import logging
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

# --- الإعدادات الأساسية ---
TOKEN = "8768205999:AAEx4VWDnAekCB--ogoKkz_wRSVUq_w4eWg"
ADMIN_ID = 7192709549  # رقمك الخاص لصلاحيات الرفع الحصرية

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
    ["السمستر الأول", "السمستر الثاني"],
    ["الرجوع للتخصصات"],
]
semesters_markup = ReplyKeyboardMarkup(semesters_keyboard, resize_keyboard=True)

# مواد السمستر الأول (مع ميكانيكا الهندسة)
sem1_subjects_keyboard = [
    ["لغة إنجليزية 1", "الحسبان"],
    ["الفيزياء", "مقدمة الحاسوب"],
    ["أعمال الورش 1", "رسم هندسي"],
    ["ميكانيكا الهندسة (ديناميكا واستاتيكا)"],
    ["الرجوع للسمسترات"],
]
sem1_subjects_markup = ReplyKeyboardMarkup(sem1_subjects_keyboard, resize_keyboard=True)

# مواد السمستر الثاني
sem2_subjects_keyboard = [
    ["لغة إنجليزية 2", "أخلاقيات المهنة"],
    ["الجبر الخطي والمعادلات التفاضلية", "برمجة الحاسوب"],
    ["أساسيات الهندسة الكهربائية", "أساسيات الالكترونيات التمثالية"],
    ["الرجوع للسمسترات"],
]
sem2_subjects_markup = ReplyKeyboardMarkup(sem2_subjects_keyboard, resize_keyboard=True)

sections_keyboard = [
    ["شيتات", "محاضرات", "امتحانات سابقة"],
    ["الرجوع للمواد"],
]
sections_markup = ReplyKeyboardMarkup(sections_keyboard, resize_keyboard=True)


# --- الدالة الموحدة والمحمية من التكرار ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user_id = update.effective_user.id
    chat_data = context.user_data

    # منع تكرار معالجة نفس النص المتلاحق السريع
    last_msg = chat_data.get("last_processed_text")
    if last_msg == text:
        return  # تجاهل التكرار لو تم استلامه في نفس اللحظة
    chat_data["last_processed_text"] = text

    if text in ["الهندسة الكهربائية (تحكم)", "الهندسة الكهربائية (قدرة)", "هندسة طبية", "هندسة شبكات"]:
        chat_data["current_specialty"] = text
        await update.message.reply_text(
            f"تم اختيار تخصص: {text}\nاختر السمستر الدراسي:",
            reply_markup=semesters_markup,
        )

    elif text == "السمستر الأول":
        chat_data["current_sem"] = "sem1"
        await update.message.reply_text(
            "اختر مادة السمستر الأول:", reply_markup=sem1_subjects_markup
        )

    elif text == "السمستر الثاني":
        chat_data["current_sem"] = "sem2"
        await update.message.reply_text(
            "اختر مادة السمستر الثاني:", reply_markup=sem2_subjects_markup
        )

    elif text in [
        "لغة إنجليزية 1", "الحسبان", "الفيزياء", "مقدمة الحاسوب", "أعمال الورش 1", "رسم هندسي",
        "ميكانيكا الهندسة (ديناميكا واستاتيكا)", "لغة إنجليزية 2", "أخلاقيات المهنة", 
        "الجبر الخطي والمعادلات التفاضلية", "برمجة الحاسوب", "أساسيات الهندسة الكهربائية", 
        "أساسيات الالكترونيات التمثالية"
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

    elif text in ["الرجوع للقائمة الرئيسية", "التعريف بالبوت", "الرجوع للتخصصات"]:
        await update.message.reply_text(
            "القائمة الرئيسية - اختر التخصص:", reply_markup=main_markup
        )

    elif text == "الرجوع للسمسترات":
        await update.message.reply_text(
            "اختر السمستر:", reply_markup=semesters_markup
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"أهلاً بك يا مهندس {user.first_name} في الأرشيف المركزي لكلية الهندسة - جامعة الخرطوم.\nاختر التخصص المناسب من لوحة المفاتيح بالأسفل:",
        reply_markup=main_markup,
    )


def main():
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

    print("البوت يعمل الآن بدون تكرار وبثبات تام...")
    app.run_polling()


if __name__ == "__main__":
    main()
