import json
import os
import re
import threading
import time

import telebot
from flask import Flask
from telebot import types

# ===== الإعدادات (من Render -> Environment) =====
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7192709549"))
# اختياري: لو تركتيه فاضي البوت بيتعرف على القناة لوحده
ENV_CHANNEL = int(os.environ.get("CHANNEL_ID", "0"))

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
TYPE_KEYS = {"شيتات": "s", "محاضرات": "l", "امتحانات سابقة": "e"}
MAIN_MENU = "القائمة الرئيسية"
ABOUT = "ℹ️ معلومات عنا"


def code_of(subject):
    m = re.search(r"EE\s*(\d{3})", subject)
    return "EE" + m.group(1)


SUBJECT_BY_CODE = {code_of(s): s for s in ALL_SUBJECTS}

# ===== قاعدة بيانات الفهرس =====
# تتخزن في رسالة مثبتة في محادثة المشرف مع البوت (عشان ما تضيع عند إعادة التشغيل)
DB_TAG = "DB:"
DB_FILE = "index.json"
db = {"channel": ENV_CHANNEL, "files": {}}
db_msg = {"id": None}
lock = threading.Lock()


def load_db():
    try:
        chat = bot.get_chat(ADMIN_ID)
        pm = getattr(chat, "pinned_message", None)
        if pm is not None and pm.text and pm.text.startswith(DB_TAG):
            data = json.loads(pm.text[len(DB_TAG):])
            db["files"] = data.get("files", {})
            if not db["channel"]:
                db["channel"] = data.get("channel", 0)
            db_msg["id"] = pm.message_id
            print("DB loaded from pinned message")
            return
    except Exception as e:
        print("load from pinned failed:", e)
    try:
        with open(DB_FILE, encoding="utf-8") as f:
            data = json.load(f)
        db["files"] = data.get("files", {})
        if not db["channel"]:
            db["channel"] = data.get("channel", 0)
        print("DB loaded from local file")
    except Exception as e:
        print("no local db:", e)


def save_db():
    with lock:
        text = DB_TAG + json.dumps(
            {"channel": db["channel"], "files": db["files"]}, separators=(",", ":")
        )
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                f.write(text[len(DB_TAG):])
        except Exception as e:
            print("local save failed:", e)
        if len(text) > 4000:
            notify("⚠️ الفهرس كبر وتعدى حد تيليجرام. كلميني عشان نغيّر طريقة التخزين.")
            return
        try:
            if db_msg["id"]:
                try:
                    bot.edit_message_text(text, ADMIN_ID, db_msg["id"])
                    return
                except Exception as e:
                    if "not modified" in str(e):
                        return
                    print("edit db failed:", e)
            m = bot.send_message(ADMIN_ID, text)
            db_msg["id"] = m.message_id
            try:
                bot.pin_chat_message(ADMIN_ID, m.message_id, disable_notification=True)
            except Exception as e:
                print("pin failed:", e)
                notify("⚠️ ما قدرت أثبّت رسالة الفهرس. ثبّتيها يدوياً (اضغطي عليها مطولاً ثم تثبيت).")
        except Exception as e:
            print("save to telegram failed:", e)


def notify(text):
    try:
        bot.send_message(ADMIN_ID, text)
    except Exception as e:
        print("notify failed:", e)


def add_file(code, tkey, mid):
    with lock:
        lst = db["files"].setdefault(code, {}).setdefault(tkey, [])
        if mid not in lst:
            lst.append(mid)
            lst.sort()
    save_db()


KEYWORDS = {
    "EE112": ["حسبان"],
    "EE113": ["فيزياء"],
    "EE114": ["مقدمة الحاسوب", "مقدمة حاسوب"],
    "EE115": ["ورش"],
    "EE116": ["رسم هندسي"],
    "EE122": ["اخلاقيات", "أخلاقيات"],
    "EE123": ["جبر", "تفاضلي"],
    "EE124": ["برمجة"],
    "EE125": ["اساسيات الهندسة الكهربائية", "أساسيات الهندسة الكهربائية"],
    "EE126": ["الكترونيات", "إلكترونيات"],
    "EE127": ["ميكانيكا", "ديناميكا", "استاتيكا"],
}


def normalize(s):
    s = (s or "").lower().replace("_", " ")
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ة", "ه"), ("ى", "ي")):
        s = s.replace(a, b)
    return s


KW_NORM = {c: [normalize(k) for k in kws] for c, kws in KEYWORDS.items()}


def guess(text):
    raw = text or ""
    norm = normalize(raw)
    code = None
    m = re.search(r"EE\s*-?\s*(\d{3})", raw, re.I)
    if m and ("EE" + m.group(1)) in SUBJECT_BY_CODE:
        code = "EE" + m.group(1)
    if code is None:
        hits = [c for c, kws in KW_NORM.items() if any(k in norm for k in kws)]
        if len(hits) == 1:
            code = hits[0]
    t = None
    if any(k in norm for k in ("امتحان", "اختبار", "exam")):
        t = "e"
    elif any(k in norm for k in ("شيت", "تمارين", "sheet", "tutorial")):
        t = "s"
    elif any(k in norm for k in ("محاضر", "lecture")):
        t = "l"
    return code, t


TYPE_NAME = {"s": "شيتات", "l": "محاضرات", "e": "امتحانات سابقة"}

# وضع التسجيل التلقائي: كل ملف يتسجل على مادة ونوع محددين
mode = {"code": None, "t": None}

# ملخص مجمّع بدل رسالة لكل ملف
summary = {"counts": {}, "timer": None}


def flush_summary():
    with lock:
        counts = dict(summary["counts"])
        summary["counts"] = {}
        summary["timer"] = None
    if not counts:
        return
    total = sum(counts.values())
    lines = [f"✅ تمت فهرسة {total} ملف:"]
    for (code, t), n in counts.items():
        lines.append(f"- {SUBJECT_BY_CODE[code]} - {TYPE_NAME[t]}: {n}")
    notify("\n".join(lines))


def note_indexed(code, t):
    with lock:
        summary["counts"][(code, t)] = summary["counts"].get((code, t), 0) + 1
        if summary["timer"] is not None:
            summary["timer"].cancel()
        summary["timer"] = threading.Timer(4.0, flush_summary)
        summary["timer"].start()


def ask_subject(mid, name):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for i, s in enumerate(ALL_SUBJECTS):
        kb.add(types.InlineKeyboardButton(s, callback_data=f"s|{mid}|{i}"))
    kb.add(types.InlineKeyboardButton("تجاهل ❌", callback_data=f"x|{mid}"))
    bot.send_message(ADMIN_ID, f"📁 ملف: {name}\nلأي مادة؟", reply_markup=kb)


def process_file(mid, name, text):
    if mode["code"] and mode["t"]:
        add_file(mode["code"], mode["t"], mid)
        note_indexed(mode["code"], mode["t"])
        return
    code, t = guess(text)
    if code and t:
        add_file(code, t, mid)
        note_indexed(code, t)
        return
    ask_subject(mid, name)


def file_name(message):
    if message.document and message.document.file_name:
        return message.document.file_name
    if message.caption:
        return message.caption[:60]
    return "ملف"


def forward_source(message):
    origin = getattr(message, "forward_origin", None)
    if origin is not None and getattr(origin, "type", "") == "channel":
        return origin.chat.id, origin.message_id
    fc = getattr(message, "forward_from_chat", None)
    fm = getattr(message, "forward_from_message_id", None)
    if fc is not None and fm:
        return fc.id, fm
    return None


# ===== استقبال ملفات القناة (فهرسة تلقائية) =====
@bot.channel_post_handler(content_types=["document", "video", "audio", "photo"])
def on_channel_post(message):
    if not db["channel"]:
        db["channel"] = message.chat.id
        save_db()
    if message.chat.id != db["channel"]:
        return
    name = file_name(message)
    process_file(message.message_id, name, name + " " + (message.caption or ""))


# ===== ملفات محوّلة (Forward) من القناة للبوت - للمشرف فقط =====
@bot.message_handler(
    content_types=["document", "video", "audio", "photo"],
    func=lambda m: m.chat.id == ADMIN_ID,
)
def on_admin_file(message):
    src = forward_source(message)
    if not src:
        bot.reply_to(message, "حوّلي (Forward) الملف من القناة للبوت بدل رفعه مباشرة هنا.")
        return
    chat_id, mid = src
    if not db["channel"]:
        db["channel"] = chat_id
        save_db()
    if chat_id != db["channel"]:
        bot.reply_to(message, "الملف ده من قناة غير القناة المسجلة.")
        return
    name = file_name(message)
    process_file(mid, name, name + " " + (message.caption or ""))


# ===== أزرار اختيار المادة والنوع (للمشرف) =====
@bot.callback_query_handler(func=lambda c: True)
def on_callback(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id)
        return
    try:
        parts = c.data.split("|")
        kind = parts[0]
        chat_id = c.message.chat.id
        msg_id = c.message.message_id
        if kind == "s":
            mid, i = int(parts[1]), int(parts[2])
            kb = types.InlineKeyboardMarkup(row_width=1)
            for j, t in enumerate(CONTENT_TYPES):
                kb.add(types.InlineKeyboardButton(t, callback_data=f"t|{mid}|{i}|{j}"))
            bot.edit_message_text(
                f"{ALL_SUBJECTS[i]}\nنوع الملف؟", chat_id, msg_id, reply_markup=kb
            )
        elif kind == "t":
            mid, i, j = int(parts[1]), int(parts[2]), int(parts[3])
            subject, ctype = ALL_SUBJECTS[i], CONTENT_TYPES[j]
            add_file(code_of(subject), TYPE_KEYS[ctype], mid)
            bot.edit_message_text(f"✅ تم: {subject} - {ctype}", chat_id, msg_id)
        elif kind == "x":
            bot.edit_message_text("تم التجاهل.", chat_id, msg_id)
        elif kind == "m":
            i = int(parts[1])
            kb = types.InlineKeyboardMarkup(row_width=1)
            for j, t in enumerate(CONTENT_TYPES):
                kb.add(types.InlineKeyboardButton(t, callback_data=f"n|{i}|{j}"))
            bot.edit_message_text(
                f"{ALL_SUBJECTS[i]}\nنوع الملفات؟", chat_id, msg_id, reply_markup=kb
            )
        elif kind == "n":
            i, j = int(parts[1]), int(parts[2])
            subject, ctype = ALL_SUBJECTS[i], CONTENT_TYPES[j]
            mode["code"] = code_of(subject)
            mode["t"] = TYPE_KEYS[ctype]
            bot.edit_message_text(
                f"✅ وضع التسجيل شغال: {subject} - {ctype}\n"
                "حوّلي (Forward) أو ارفعي الملفات الآن وكلها تتسجل هنا.\n"
                "للإيقاف اكتبي /modeoff",
                chat_id,
                msg_id,
            )
    except Exception as e:
        print("callback error:", e)
    bot.answer_callback_query(c.id)


# ===== القوائم =====
user_subject = {}


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


def send_files(message, subject, ctype):
    ids = db["files"].get(code_of(subject), {}).get(TYPE_KEYS[ctype], [])
    channel = db["channel"]
    if not ids or not channel:
        bot.reply_to(message, f"لا توجد ملفات ({ctype}) لهذه المادة حالياً، سيتم رفعها قريباً.")
        return
    bot.reply_to(message, f"جاري إرسال {len(ids)} ملف... ⏳")
    for mid in ids:
        try:
            bot.copy_message(message.chat.id, channel, mid)
            time.sleep(0.4)
        except Exception as e:
            print("copy_message failed:", mid, e)


# ===== الأوامر =====
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "مرحباً بك يا مهندس في بوت أرشيف هندسة جامعة الخرطوم! 🎓\nاختر التخصص المطلوب:",
        reply_markup=main_markup(),
    )


@bot.message_handler(commands=["mode"])
def set_mode(message):
    if message.chat.id != ADMIN_ID:
        return
    kb = types.InlineKeyboardMarkup(row_width=1)
    for i, s in enumerate(ALL_SUBJECTS):
        kb.add(types.InlineKeyboardButton(s, callback_data=f"m|{i}"))
    bot.send_message(ADMIN_ID, "اختاري المادة اللي حترفعي ملفاتها:", reply_markup=kb)


@bot.message_handler(commands=["modeoff"])
def mode_off(message):
    if message.chat.id != ADMIN_ID:
        return
    mode["code"] = None
    mode["t"] = None
    bot.reply_to(message, "تم إيقاف وضع التسجيل التلقائي.")


@bot.message_handler(commands=["stats"])
def stats(message):
    if message.chat.id != ADMIN_ID:
        return
    lines = [f"القناة: {db['channel'] or 'غير محددة'}"]
    for s in ALL_SUBJECTS:
        d = db["files"].get(code_of(s), {})
        total = sum(len(v) for v in d.values())
        if total:
            lines.append(
                f"{s}: شيتات {len(d.get('s', []))} | محاضرات {len(d.get('l', []))} | امتحانات {len(d.get('e', []))}"
            )
    bot.reply_to(message, "\n".join(lines))


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
        bot.reply_to(message, f"{text}: اختر المادة:", reply_markup=subjects_markup(text))

    elif text in ALL_SUBJECTS:
        user_subject[message.chat.id] = text
        bot.reply_to(
            message,
            f"أنت اخترت مادة: {text}\nاختر نوع المحتوى المطلوب:",
            reply_markup=content_markup(),
        )

    elif text in CONTENT_TYPES:
        subject = user_subject.get(message.chat.id)
        if not subject:
            bot.reply_to(message, "اختر المادة أولاً من القائمة الرئيسية.", reply_markup=main_markup())
        else:
            send_files(message, subject, text)

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
load_db()
print("Bot is polling...")
bot.infinity_polling(skip_pending=True, allowed_updates=["message", "callback_query", "channel_post"])
