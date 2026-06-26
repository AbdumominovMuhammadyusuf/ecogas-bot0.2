"""
OSAGO Telegram Bot — EcoGas Avtoservis
"""

import logging
import re
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)

# ─── SOZLAMALAR ───────────────────────────────────────────────
BOT_TOKEN = "8915481456:AAHuDL19HRV91gURTF6XiYfa5BUcbJGwnAs"
OPERATOR_CHAT_ID = "8498320053"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── HOLATLAR ─────────────────────────────────────────────────
(
    LANG,
    STEP0_PHONE,
    STEP1_PLATE,
    STEP1_TECHPASS,
    STEP2_INSURANCE_TYPE,
    STEP3_OWNER_PASSPORT,
    STEP3_OWNER_JSHIR,
    STEP3_OWNER_BIRTH,
    STEP3_OWNER_IN_POLICY,
    STEP4_DRIVER_PASSPORT,
    STEP4_DRIVER_JSHIR,
    STEP4_DRIVER_BIRTH,
    STEP4_MORE_DRIVERS,
    STEP5_DURATION,
    STEP6_PAYMENT,
    STEP6_CHECK,
) = range(16)

# ─── MATNLAR ──────────────────────────────────────────────────
TEXTS = {
    "uz": {
        "welcome": (
            "Assalomu alaykum! *EcoGas Avtoservis* botiga xush kelibsiz! 🎉\n\n"
            "Bu bot orqali OSAGO sug'urtasini tez va oson rasmiylashtirishingiz mumkin.\n\n"
            "✅ Hujjat yig'ish shart emas — faqat raqamlarni kiriting\n"
            "✅ Sug'urtangiz 30 daqiqa ichida tayyor bo'ladi\n"
            "✅ PDF polis Telegram orqali yuboriladi\n\n"
            "🏢 *EcoGas Avtoservis* — avtomobil xizmati va sug'urta rasmiylashtirishda ishonchli hamkoringiz!\n\n"
            "📌 Boshlash uchun tugmani bosing 👇"
        ),
        "start_btn": "🚀 Boshlash",
        "ask_phone": (
            "📱 *Telefon raqamingizni yuboring*\n\n"
            "Quyidagi tugmani bosing yoki qo'lda kiriting\n"
            "_Masalan: +998901234567_\n\n"
            "💡 Operator polisni rasmiylashtirish jarayonida yoki tayyor bo'lganda shu raqam orqali siz bilan bog'lanadi"
        ),
        "phone_btn": "📱 Raqamimni yuborish",
        "error_phone": "⚠️ Noto'g'ri format!\nMasalan: *+998901234567*\nQaytadan kiriting:",

        "step1_header": "📋 *1-QADAM: Mashina ma'lumotlari*\n━━━━━━━━━━━━━━━━━━",
        "ask_plate": (
            "🚗 Mashinangizning *davlat raqami*ni kiriting\n\n"
            "📌 Format: `01A001AA`\n"
            "_2 raqam + 1 harf + 3 raqam + 2 harf_"
        ),
        "ask_techpass": (
            "📄 Endi *texpassport raqami*ni kiriting\n\n"
            "💡 Texpassportingizning *orqa tomonida* `AA` bilan boshlanadigan raqamlar bor — o'shani kiriting\n\n"
            "📌 Format: `AAF1234567`\n"
            "_3 harf + 7 raqam_"
        ),
        "error_plate": "⚠️ Noto'g'ri format!\n\n📌 To'g'ri format: `01A001AA`\nQaytadan kiriting:",
        "error_techpass": "⚠️ Noto'g'ri format!\n\n📌 To'g'ri format: `AAF1234567`\nQaytadan kiriting:",

        "step2_header": "🛡️ *2-QADAM: Sug'urta turi*\n━━━━━━━━━━━━━━━━━━",
        "ask_ins_type": (
            "Sug'urta turini tanlang:\n\n"
            "👥 *Cheklangan* — faqat polis ichidagi haydovchilar haydaydi\n"
            "_haydovchilar ismi kiritiladi_\n\n"
            "🌐 *Cheklanmagan* — istalgan haydovchi haydashi mumkin\n"
            "_haydovchi ma'lumotlari kiritilmaydi_"
        ),
        "limited": "👥 Cheklangan",
        "unlimited": "🌐 Cheklanmagan",

        "step3_header": "👤 *3-QADAM: Mashina egasi ma'lumotlari*\n━━━━━━━━━━━━━━━━━━",
        "step3_intro": "Endi mashina egasining ma'lumotlarini *birma-bir* kiritamiz 👇",
        "ask_owner_passport": (
            "🪪 Egasining *pasport seriya va raqami*ni kiriting\n\n"
            "📌 Format: `AA1234567`\n"
            "_2 harf + 7 raqam_"
        ),
        "ask_owner_jshir": (
            "🔢 Egasining *JSHIR*ini kiriting\n\n"
            "📌 *14 ta raqam*\n"
            "💡 Pasport orqasida yoki my.gov.uz da topasiz"
        ),
        "ask_owner_birth": (
            "📅 Egasining *tug'ilgan sanasi*ni kiriting\n\n"
            "📌 Format: `KUN.OY.YIL`\n"
            "Masalan: `15.06.1985`"
        ),
        "ask_owner_in_policy": (
            "❓ Mashina egasi ham o'zi haydaydimi?\n\n"
            "_Ha deb tanlasangiz, egasi ham haydovchilar ro'yxatiga kiritiladi_"
        ),
        "yes": "✅ Ha, o'zi ham haydaydi",
        "no": "❌ Yo'q",
        "error_passport": "⚠️ Noto'g'ri format!\n\n📌 To'g'ri format: `AA1234567`\nQaytadan kiriting:",
        "error_jshir": "⚠️ JSHIR *14 ta raqam* bo'lishi kerak!\nQaytadan kiriting:",
        "error_date": "⚠️ Noto'g'ri format!\n\n📌 To'g'ri format: `15.06.1985`\nQaytadan kiriting:",

        "step4_header": "👥 *4-QADAM: Haydovchilar ma'lumotlari*\n━━━━━━━━━━━━━━━━━━",
        "step4_intro": "Endi har bir haydovchining ma'lumotlarini *birma-bir* kiritamiz 👇",
        "ask_driver_passport": (
            "🪪 Haydovchining *pasport seriya va raqami*\n\n"
            "📌 Format: `AA1234567`"
        ),
        "ask_driver_jshir": "🔢 Haydovchining *JSHIR*i\n\n📌 *14 ta raqam*",
        "ask_driver_birth": (
            "📅 Haydovchining *tug'ilgan sanasi*\n\n"
            "📌 Format: `KUN.OY.YIL`\n"
            "Masalan: `20.03.1990`"
        ),
        "driver_added": "✅ *{n}-haydovchi qo'shildi!*\n\nYana haydovchi qo'shilsinmi?",
        "add_driver": "➕ Yana haydovchi qo'shish",
        "done_drivers": "✅ Haydovchilar tayyor",

        "step5_header": "📆 *5-QADAM: Sug'urta muddati*\n━━━━━━━━━━━━━━━━━━",
        "ask_duration": (
            "Sug'urta muddatini tanlang:\n\n"
            "📅 *6 oy* — qisqa muddat uchun\n"
            "📅 *1 yil* — tejamkorroq variant"
        ),
        "6months": "📅 6 oy",
        "1year": "📅 1 yil",

        "step6_header": "💳 *6-QADAM: To'lov*\n━━━━━━━━━━━━━━━━━━",
        "ask_payment": (
            "✅ *Barcha ma'lumotlar qabul qilindi!*\n\n"
            "⏳ Operator ma'lumotlarni tekshirib, narxni hisoblab,\n"
            "to'lov linkini yoki QR kodni *shu chatga* yuboradi.\n\n"
            "💳 To'lov turini tanlang:"
        ),
        "pay_card": "💳 Bank kartasi",
        "pay_click": "📱 Click",
        "pay_payme": "📱 Payme",
        "pay_transfer": "🏦 Bank o'tkazmasi",

        "ask_check": (
            "📎 To'lovni amalga oshirgach *chek rasmini* yuboring 👇\n\n"
            "_(Chekni screenshot qilib yuboring)_"
        ),
        "check_received": (
            "✅ *Chek qabul qilindi! Rahmat.*\n\n"
            "⏳ Operatorimiz ma'lumotlarni tekshirmoqda...\n\n"
            "🏢 *EcoGas Avtoservis* — biz har doim siz uchun!\n"
            "📞 +998 91 078 88 78\n"
            "📞 +998 90 625 00 07\n"
            "💬 Telegram: @EndlessCompanyADMIN\n\n"
            "📄 OSAGO polisingiz *30 daqiqa ichida* PDF ko'rinishida shu chatga yuboriladi!"
        ),

        "cancel_btn": "❌ Bekor qilish",
        "cancelled": "❌ *Ariza bekor qilindi.*\n\nQaytadan boshlash uchun /start bosing.",

        "final": (
            "🎉 *Tabriklaymiz! Sug'urtangiz rasmiylashtirildi!*\n\n"
            "📄 PDF polisingizni saqlang yoki chop ettiring.\n"
            "🚗 Xavfsiz va omadli yo'l!\n\n"
            "🏢 *EcoGas Avtoservis* xizmatidan foydalanganingiz uchun *rahmat!* 🙏\n"
            "Siz bilan hamkorlik qilganimizdan mamnunmiz!\n\n"
            "📞 +998 91 078 88 78\n"
            "📞 +998 90 625 00 07\n"
            "💬 Telegram: @EndlessCompanyADMIN\n\n"
            "Yana murojaat uchun: /start"
        ),
    },

    "ru": {
        "welcome": (
            "Здравствуйте! Добро пожаловать в бот *EcoGas Avtoservis*! 🎉\n\n"
            "С помощью этого бота вы можете быстро и легко оформить страховку ОСАГО.\n\n"
            "✅ Не нужно собирать документы — просто вводите данные\n"
            "✅ Страховка готова за 30 минут\n"
            "✅ PDF-полис отправляется в Telegram\n\n"
            "🏢 *EcoGas Avtoservis* — надёжный партнёр в автосервисе и страховании!\n\n"
            "📌 Нажмите кнопку ниже, чтобы начать 👇"
        ),
        "start_btn": "🚀 Начать",
        "ask_phone": (
            "📱 *Отправьте ваш номер телефона*\n\n"
            "Нажмите кнопку или введите вручную\n"
            "_Например: +998901234567_\n\n"
            "💡 Оператор свяжется с вами по этому номеру в процессе оформления"
        ),
        "phone_btn": "📱 Отправить номер",
        "error_phone": "⚠️ Неверный формат!\nНапример: *+998901234567*\nВведите снова:",

        "step1_header": "📋 *ШАГ 1: Данные автомобиля*\n━━━━━━━━━━━━━━━━━━",
        "ask_plate": (
            "🚗 Введите *государственный номер* автомобиля\n\n"
            "📌 Формат: `01A001AA`\n"
            "_2 цифры + 1 буква + 3 цифры + 2 буквы_"
        ),
        "ask_techpass": (
            "📄 Теперь введите номер *техпаспорта*\n\n"
            "💡 На *обратной стороне* техпаспорта есть номер, начинающийся с `AA` — введите его\n\n"
            "📌 Формат: `AAF1234567`\n"
            "_3 буквы + 7 цифр_"
        ),
        "error_plate": "⚠️ Неверный формат!\n\n📌 Правильный формат: `01A001AA`\nВведите снова:",
        "error_techpass": "⚠️ Неверный формат!\n\n📌 Правильный формат: `AAF1234567`\nВведите снова:",

        "step2_header": "🛡️ *ШАГ 2: Тип страховки*\n━━━━━━━━━━━━━━━━━━",
        "ask_ins_type": (
            "Выберите тип страховки:\n\n"
            "👥 *Ограниченная* — за рулём только вписанные водители\n"
            "_данные водителей вводятся_\n\n"
            "🌐 *Неограниченная* — за рулём может быть любой водитель\n"
            "_данные водителей не нужны_"
        ),
        "limited": "👥 Ограниченная",
        "unlimited": "🌐 Неограниченная",

        "step3_header": "👤 *ШАГ 3: Данные владельца автомобиля*\n━━━━━━━━━━━━━━━━━━",
        "step3_intro": "Теперь вводим данные владельца автомобиля *по одному* 👇",
        "ask_owner_passport": (
            "🪪 Введите *серию и номер паспорта* владельца\n\n"
            "📌 Формат: `AA1234567`\n"
            "_2 буквы + 7 цифр_"
        ),
        "ask_owner_jshir": (
            "🔢 Введите *ПИНФЛ* владельца\n\n"
            "📌 *14 цифр*\n"
            "💡 Указан на обороте паспорта или на my.gov.uz"
        ),
        "ask_owner_birth": (
            "📅 Введите *дату рождения* владельца\n\n"
            "📌 Формат: `ДЕНЬ.МЕСЯЦ.ГОД`\n"
            "Например: `15.06.1985`"
        ),
        "ask_owner_in_policy": (
            "❓ Владелец тоже будет за рулём?\n\n"
            "_Если да — владелец будет включён в список водителей_"
        ),
        "yes": "✅ Да, тоже водит",
        "no": "❌ Нет",
        "error_passport": "⚠️ Неверный формат!\n\n📌 Правильный формат: `AA1234567`\nВведите снова:",
        "error_jshir": "⚠️ ПИНФЛ должен содержать *14 цифр*!\nВведите снова:",
        "error_date": "⚠️ Неверный формат!\n\n📌 Правильный формат: `15.06.1985`\nВведите снова:",

        "step4_header": "👥 *ШАГ 4: Данные водителей*\n━━━━━━━━━━━━━━━━━━",
        "step4_intro": "Теперь вводим данные каждого водителя *по одному* 👇",
        "ask_driver_passport": (
            "🪪 *Серия и номер паспорта* водителя\n\n"
            "📌 Формат: `AA1234567`"
        ),
        "ask_driver_jshir": "🔢 *ПИНФЛ* водителя\n\n📌 *14 цифр*",
        "ask_driver_birth": (
            "📅 *Дата рождения* водителя\n\n"
            "📌 Формат: `ДЕНЬ.МЕСЯЦ.ГОД`\n"
            "Например: `20.03.1990`"
        ),
        "driver_added": "✅ *Водитель {n} добавлен!*\n\nДобавить ещё одного водителя?",
        "add_driver": "➕ Добавить водителя",
        "done_drivers": "✅ Водители готовы",

        "step5_header": "📆 *ШАГ 5: Срок страховки*\n━━━━━━━━━━━━━━━━━━",
        "ask_duration": (
            "Выберите срок страховки:\n\n"
            "📅 *6 месяцев* — для краткосрочного периода\n"
            "📅 *1 год* — более выгодный вариант"
        ),
        "6months": "📅 6 месяцев",
        "1year": "📅 1 год",

        "step6_header": "💳 *ШАГ 6: Оплата*\n━━━━━━━━━━━━━━━━━━",
        "ask_payment": (
            "✅ *Все данные приняты!*\n\n"
            "⏳ Оператор проверит данные, рассчитает стоимость\n"
            "и пришлёт ссылку или QR-код для оплаты *в этот чат*.\n\n"
            "💳 Выберите способ оплаты:"
        ),
        "pay_card": "💳 Банковская карта",
        "pay_click": "📱 Click",
        "pay_payme": "📱 Payme",
        "pay_transfer": "🏦 Банковский перевод",

        "ask_check": (
            "📎 После оплаты отправьте *скриншот чека* 👇\n\n"
            "_(Сделайте скриншот и отправьте в этот чат)_"
        ),
        "check_received": (
            "✅ *Чек получен! Спасибо.*\n\n"
            "⏳ Оператор проверяет данные...\n\n"
            "🏢 *EcoGas Avtoservis* — мы всегда для вас!\n"
            "📞 +998 91 078 88 78\n"
            "📞 +998 90 625 00 07\n"
            "💬 Telegram: @EndlessCompanyADMIN\n\n"
            "📄 Ваш полис ОСАГО будет отправлен в формате PDF *в течение 30 минут*!"
        ),

        "cancel_btn": "❌ Отмена",
        "cancelled": "❌ *Заявка отменена.*\n\nДля начала нажмите /start.",

        "final": (
            "🎉 *Поздравляем! Страховка оформлена!*\n\n"
            "📄 Сохраните PDF-полис или распечатайте его.\n"
            "🚗 Счастливого и безопасного пути!\n\n"
            "🏢 *EcoGas Avtoservis* — спасибо за доверие! 🙏\n"
            "Рады сотрудничеству с вами!\n\n"
            "📞 +998 91 078 88 78\n"
            "📞 +998 90 625 00 07\n"
            "💬 Telegram: @EndlessCompanyADMIN\n\n"
            "Для новой заявки: /start"
        ),
    }
}

# ─── YORDAMCHI FUNKSIYALAR ────────────────────────────────────

def t(lang, key, **kwargs):
    text = TEXTS.get(lang, TEXTS["uz"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

def get_lang(context):
    return context.user_data.get("lang", "uz")

def cancel_kb(lang):
    return ReplyKeyboardMarkup([[t(lang, "cancel_btn")]], resize_keyboard=True)

def is_cancel(text, lang):
    return text in ["❌ Bekor qilish", "❌ Отмена"]

def ok_plate(s):
    return bool(re.match(r"^\d{2}[A-Za-z]\d{3}[A-Za-z]{2}$", s.strip().upper()))

def ok_techpass(s):
    return bool(re.match(r"^[A-Za-z]{3}\d{7}$", s.strip().upper()))

def ok_passport(s):
    return bool(re.match(r"^[A-Za-z]{2}\d{7}$", s.strip().upper()))

def ok_jshir(s):
    return s.strip().isdigit() and len(s.strip()) == 14

def ok_date(s):
    return bool(re.match(r"^\d{2}\.\d{2}\.\d{4}$", s.strip()))

def ok_phone(s):
    c = re.sub(r"[\s\-\(\)]", "", s)
    return bool(re.match(r"^(\+998|998|0)\d{9}$", c))

def build_summary(data, lang):
    drivers = data.get("drivers", [])
    drv_text = ""
    for i, d in enumerate(drivers, 1):
        drv_text += f"\n  👤 {i}-haydovchi:\n  Pasport: `{d['passport']}`\n  JSHIR: `{d['jshir']}`\n  T.sana: {d['birth']}\n"

    ins = ("👥 Cheklangan" if data.get("ins_type") == "limited" else "🌐 Cheklanmagan") if lang == "uz" \
        else ("👥 Ограниченная" if data.get("ins_type") == "limited" else "🌐 Неограниченная")
    dur = ("6 oy" if data.get("duration") == "6" else "1 yil") if lang == "uz" \
        else ("6 месяцев" if data.get("duration") == "6" else "1 год")
    pay = {"card": "💳 Bank kartasi", "click": "📱 Click", "payme": "📱 Payme", "transfer": "🏦 Bank o'tkazmasi"}.get(data.get("payment_method", ""), "—")

    return (
        f"🆕 *YANGI ARIZA*\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        f"👤 @{data.get('username', '—')} (ID: `{data.get('user_id', '—')}`)\n"
        f"📱 Tel: `{data.get('phone', '—')}`\n"
        f"🌐 Til: {'O\'zbek 🇺🇿' if lang == 'uz' else 'Rus 🇷🇺'}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🚗 *MASHINA*\n"
        f"Raqam: `{data.get('plate', '—')}`\n"
        f"Texpassport: `{data.get('techpass', '—')}`\n\n"
        f"🛡️ *SUG'URTA TURI:* {ins}\n\n"
        f"👤 *EGASI*\n"
        f"Pasport: `{data.get('owner_passport', '—')}`\n"
        f"JSHIR: `{data.get('owner_jshir', '—')}`\n"
        f"T.sana: {data.get('owner_birth', '—')}\n"
        f"Polis ichida: {'✅ Ha' if data.get('owner_in_policy') else '❌ Yoq'}\n"
        + (f"\n👥 *HAYDOVCHILAR:*{drv_text}" if drivers else "") +
        f"\n📆 *MUDDAT:* {dur}\n"
        f"💳 *TO'LOV:* {pay}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⬆️ Ma'lumotlarni kiriting va to'lov linkini yuboring\n"
        f"📨 Foydalanuvchi ID: `{data.get('user_id', '—')}`"
    )

# ─── HANDLERLAR ───────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ])
    await update.message.reply_text(
        "🚗 *EcoGas Avtoservis — OSAGO*\n\nTilni tanlang / Выберите язык:",
        parse_mode="Markdown", reply_markup=kb
    )
    return LANG

async def lang_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = "uz" if q.data == "lang_uz" else "ru"
    context.user_data["lang"] = lang
    context.user_data["user_id"] = q.from_user.id
    context.user_data["username"] = q.from_user.username or q.from_user.first_name
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(t(lang, "start_btn"), callback_data="go_phone")]])
    await q.edit_message_text(t(lang, "welcome"), parse_mode="Markdown", reply_markup=kb)
    return LANG

async def go_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    await q.edit_message_text(t(lang, "welcome"), parse_mode="Markdown")
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(t(lang, "phone_btn"), request_contact=True)], [t(lang, "cancel_btn")]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await q.message.reply_text(t(lang, "ask_phone"), parse_mode="Markdown", reply_markup=kb)
    return STEP0_PHONE

async def step0_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    if update.message.contact:
        phone = update.message.contact.phone_number
        if not phone.startswith("+"): phone = "+" + phone
        context.user_data["phone"] = phone
    else:
        text = update.message.text.strip()
        if is_cancel(text, lang): return await cancel(update, context)
        if not ok_phone(text):
            await update.message.reply_text(t(lang, "error_phone"), parse_mode="Markdown")
            return STEP0_PHONE
        context.user_data["phone"] = text
    await update.message.reply_text(t(lang, "step1_header"), parse_mode="Markdown", reply_markup=cancel_kb(lang))
    await update.message.reply_text(t(lang, "ask_plate"), parse_mode="Markdown")
    return STEP1_PLATE

async def step1_plate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = update.message.text.strip()
    if is_cancel(text, lang): return await cancel(update, context)
    if not ok_plate(text):
        await update.message.reply_text(t(lang, "error_plate"), parse_mode="Markdown")
        return STEP1_PLATE
    context.user_data["plate"] = text.upper()
    await update.message.reply_text(t(lang, "ask_techpass"), parse_mode="Markdown")
    return STEP1_TECHPASS

async def step1_techpass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = update.message.text.strip()
    if is_cancel(text, lang): return await cancel(update, context)
    if not ok_techpass(text):
        await update.message.reply_text(t(lang, "error_techpass"), parse_mode="Markdown")
        return STEP1_TECHPASS
    context.user_data["techpass"] = text.upper()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "limited"), callback_data="ins_limited")],
        [InlineKeyboardButton(t(lang, "unlimited"), callback_data="ins_unlimited")]
    ])
    await update.message.reply_text(t(lang, "step2_header"), parse_mode="Markdown")
    await update.message.reply_text(t(lang, "ask_ins_type"), parse_mode="Markdown", reply_markup=kb)
    return STEP2_INSURANCE_TYPE

async def step2_insurance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    context.user_data["ins_type"] = "limited" if q.data == "ins_limited" else "unlimited"
    context.user_data["drivers"] = []
    chosen = t(lang, "limited") if q.data == "ins_limited" else t(lang, "unlimited")
    await q.edit_message_text(t(lang, "ask_ins_type") + f"\n\n✅ *{chosen}*", parse_mode="Markdown")
    await q.message.reply_text(t(lang, "step3_header"), parse_mode="Markdown")
    await q.message.reply_text(t(lang, "step3_intro"), parse_mode="Markdown")
    await q.message.reply_text(t(lang, "ask_owner_passport"), parse_mode="Markdown", reply_markup=cancel_kb(lang))
    return STEP3_OWNER_PASSPORT

async def step3_owner_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = update.message.text.strip()
    if is_cancel(text, lang): return await cancel(update, context)
    if not ok_passport(text):
        await update.message.reply_text(t(lang, "error_passport"), parse_mode="Markdown")
        return STEP3_OWNER_PASSPORT
    context.user_data["owner_passport"] = text.upper()
    await update.message.reply_text(t(lang, "ask_owner_jshir"), parse_mode="Markdown")
    return STEP3_OWNER_JSHIR

async def step3_owner_jshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = update.message.text.strip()
    if is_cancel(text, lang): return await cancel(update, context)
    if not ok_jshir(text):
        await update.message.reply_text(t(lang, "error_jshir"), parse_mode="Markdown")
        return STEP3_OWNER_JSHIR
    context.user_data["owner_jshir"] = text
    await update.message.reply_text(t(lang, "ask_owner_birth"), parse_mode="Markdown")
    return STEP3_OWNER_BIRTH

async def step3_owner_birth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = update.message.text.strip()
    if is_cancel(text, lang): return await cancel(update, context)
    if not ok_date(text):
        await update.message.reply_text(t(lang, "error_date"), parse_mode="Markdown")
        return STEP3_OWNER_BIRTH
    context.user_data["owner_birth"] = text
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "yes"), callback_data="owner_yes")],
        [InlineKeyboardButton(t(lang, "no"), callback_data="owner_no")]
    ])
    await update.message.reply_text(t(lang, "ask_owner_in_policy"), parse_mode="Markdown", reply_markup=kb)
    return STEP3_OWNER_IN_POLICY

async def step3_owner_in_policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    context.user_data["owner_in_policy"] = (q.data == "owner_yes")
    await q.edit_message_text("✅ " + ("Saqlandi" if lang == "uz" else "Сохранено"), parse_mode="Markdown")

    if context.user_data.get("ins_type") == "unlimited":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(lang, "6months"), callback_data="dur_6")],
            [InlineKeyboardButton(t(lang, "1year"), callback_data="dur_12")]
        ])
        await q.message.reply_text(t(lang, "step5_header"), parse_mode="Markdown")
        await q.message.reply_text(t(lang, "ask_duration"), parse_mode="Markdown", reply_markup=kb)
        return STEP5_DURATION

    await q.message.reply_text(t(lang, "step4_header"), parse_mode="Markdown")
    await q.message.reply_text(t(lang, "step4_intro"), parse_mode="Markdown")
    await q.message.reply_text(t(lang, "ask_driver_passport"), parse_mode="Markdown", reply_markup=cancel_kb(lang))
    return STEP4_DRIVER_PASSPORT

async def step4_driver_passport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = update.message.text.strip()
    if is_cancel(text, lang): return await cancel(update, context)
    if not ok_passport(text):
        await update.message.reply_text(t(lang, "error_passport"), parse_mode="Markdown")
        return STEP4_DRIVER_PASSPORT
    context.user_data["_drv"] = {"passport": text.upper()}
    await update.message.reply_text(t(lang, "ask_driver_jshir"), parse_mode="Markdown")
    return STEP4_DRIVER_JSHIR

async def step4_driver_jshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = update.message.text.strip()
    if is_cancel(text, lang): return await cancel(update, context)
    if not ok_jshir(text):
        await update.message.reply_text(t(lang, "error_jshir"), parse_mode="Markdown")
        return STEP4_DRIVER_JSHIR
    context.user_data["_drv"]["jshir"] = text
    await update.message.reply_text(t(lang, "ask_driver_birth"), parse_mode="Markdown")
    return STEP4_DRIVER_BIRTH

async def step4_driver_birth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    text = update.message.text.strip()
    if is_cancel(text, lang): return await cancel(update, context)
    if not ok_date(text):
        await update.message.reply_text(t(lang, "error_date"), parse_mode="Markdown")
        return STEP4_DRIVER_BIRTH
    context.user_data["_drv"]["birth"] = text
    context.user_data["drivers"].append(context.user_data.pop("_drv"))
    n = len(context.user_data["drivers"])
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "add_driver"), callback_data="more_yes")],
        [InlineKeyboardButton(t(lang, "done_drivers"), callback_data="more_no")]
    ])
    await update.message.reply_text(t(lang, "driver_added", n=n), parse_mode="Markdown", reply_markup=kb)
    return STEP4_MORE_DRIVERS

async def step4_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    if q.data == "more_yes":
        await q.edit_message_text(t(lang, "ask_driver_passport"), parse_mode="Markdown")
        await q.message.reply_text(t(lang, "ask_driver_passport"), parse_mode="Markdown", reply_markup=cancel_kb(lang))
        return STEP4_DRIVER_PASSPORT
    await q.edit_message_text("✅ " + ("Haydovchilar saqlandi" if lang == "uz" else "Водители сохранены"), parse_mode="Markdown")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "6months"), callback_data="dur_6")],
        [InlineKeyboardButton(t(lang, "1year"), callback_data="dur_12")]
    ])
    await q.message.reply_text(t(lang, "step5_header"), parse_mode="Markdown")
    await q.message.reply_text(t(lang, "ask_duration"), parse_mode="Markdown", reply_markup=kb)
    return STEP5_DURATION

async def step5_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    context.user_data["duration"] = "6" if q.data == "dur_6" else "12"
    chosen = t(lang, "6months") if q.data == "dur_6" else t(lang, "1year")
    await q.edit_message_text(t(lang, "ask_duration") + f"\n\n✅ *{chosen}*", parse_mode="Markdown")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "pay_card"), callback_data="pay_card")],
        [InlineKeyboardButton(t(lang, "pay_click"), callback_data="pay_click"),
         InlineKeyboardButton(t(lang, "pay_payme"), callback_data="pay_payme")],
        [InlineKeyboardButton(t(lang, "pay_transfer"), callback_data="pay_transfer")]
    ])
    await q.message.reply_text(t(lang, "step6_header"), parse_mode="Markdown")
    await q.message.reply_text(t(lang, "ask_payment"), parse_mode="Markdown", reply_markup=kb)
    return STEP6_PAYMENT

async def step6_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    context.user_data["payment_method"] = q.data.replace("pay_", "")

    # Operatorga xabar
    summary = build_summary(context.user_data, lang)
    try:
        await q.get_bot().send_message(chat_id=OPERATOR_CHAT_ID, text=summary, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Operator xato: {e}")

    pay_labels = {"pay_card": t(lang,"pay_card"), "pay_click": t(lang,"pay_click"),
                  "pay_payme": t(lang,"pay_payme"), "pay_transfer": t(lang,"pay_transfer")}
    await q.edit_message_text(
        t(lang, "ask_payment") + f"\n\n✅ *{pay_labels.get(q.data, '')}*",
        parse_mode="Markdown"
    )
    await q.message.reply_text(
        t(lang, "ask_check"),
        parse_mode="Markdown",
        reply_markup=cancel_kb(lang)
    )
    return STEP6_CHECK

async def step6_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)

    if update.message.text and is_cancel(update.message.text, lang):
        return await cancel(update, context)

    # Chek rasm yoki dokument bo'lishi kerak
    if not (update.message.photo or update.message.document):
        await update.message.reply_text(
            "📎 " + ("Chek rasmini yuboring 👇" if lang == "uz" else "Отправьте фото чека 👇"),
            parse_mode="Markdown"
        )
        return STEP6_CHECK

    # Operatorga chekni forward qilish
    try:
        user_id = context.user_data.get("user_id")
        username = context.user_data.get("username", "—")
        plate = context.user_data.get("plate", "—")
        await update.message.forward(chat_id=OPERATOR_CHAT_ID)
        await update.get_bot().send_message(
            chat_id=OPERATOR_CHAT_ID,
            text=(
                f"💳 *CHEK YUBORILDI*\n"
                f"👤 @{username} (ID: `{user_id}`)\n"
                f"🚗 {plate}\n\n"
                f"⬆️ *PDF POLISNI YUBORING!*"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Chek forward xato: {e}")

    await update.message.reply_text(
        t(lang, "check_received"),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    context.user_data.clear()
    await update.message.reply_text(t(lang, "cancelled"), parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(
        ("ℹ️ *Yordam*\n\n/start — OSAGO boshlash\n/cancel — Bekor qilish\n\n"
         "📞 +998 91 078 88 78\n📞 +998 90 625 00 07\n💬 @EndlessCompanyADMIN"
         if lang == "uz" else
         "ℹ️ *Помощь*\n\n/start — Начать ОСАГО\n/cancel — Отменить\n\n"
         "📞 +998 91 078 88 78\n📞 +998 90 625 00 07\n💬 @EndlessCompanyADMIN"),
        parse_mode="Markdown"
    )

# ─── ASOSIY ───────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [
                CallbackQueryHandler(lang_chosen, pattern="^lang_"),
                CallbackQueryHandler(go_phone, pattern="^go_phone$"),
            ],
            STEP0_PHONE: [
                MessageHandler(filters.CONTACT, step0_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, step0_phone),
            ],
            STEP1_PLATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, step1_plate)],
            STEP1_TECHPASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, step1_techpass)],
            STEP2_INSURANCE_TYPE: [CallbackQueryHandler(step2_insurance, pattern="^ins_")],
            STEP3_OWNER_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step3_owner_passport)],
            STEP3_OWNER_JSHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, step3_owner_jshir)],
            STEP3_OWNER_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, step3_owner_birth)],
            STEP3_OWNER_IN_POLICY: [CallbackQueryHandler(step3_owner_in_policy, pattern="^owner_")],
            STEP4_DRIVER_PASSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, step4_driver_passport)],
            STEP4_DRIVER_JSHIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, step4_driver_jshir)],
            STEP4_DRIVER_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, step4_driver_birth)],
            STEP4_MORE_DRIVERS: [CallbackQueryHandler(step4_more, pattern="^more_")],
            STEP5_DURATION: [CallbackQueryHandler(step5_duration, pattern="^dur_")],
            STEP6_PAYMENT: [CallbackQueryHandler(step6_payment, pattern="^pay_")],
            STEP6_CHECK: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, step6_check),
                MessageHandler(filters.TEXT & ~filters.COMMAND, step6_check),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Regex("^(❌ Bekor qilish|❌ Отмена)$"), cancel),
        ],
        per_message=False,
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_cmd))
    logger.info("✅ EcoGas Avtoservis boti ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
