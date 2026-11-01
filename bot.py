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
