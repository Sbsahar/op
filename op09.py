# tstop.py - الكود المدمج في ملف واحد لتجنب التعارض

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import sqlite3
import random
import string
import time
import threading
import os
import api_handler  # استيراد الملف الجديد للتعامل مع الـ API
from datetime import datetime, timedelta

# استبدل هذه المتغيرات
BOT_TOKEN = '7524766252:AAFfFAFCMrtloJeCFI_4auUD_ahvuyaONzQ'
DEVELOPER_ID = 6789179634  # ايدي المطور
GROUP_ID = -1002091669531  # ID المجموعة لإرسال الطلبات
BOT_USERNAME = 'Chatgpt_4bbot'  # استبدل بيوزر البوت الخاص بك

bot = telebot.TeleBot(BOT_TOKEN)

# إعداد أوامر البوت
def set_bot_commands():
    commands = [
        BotCommand("start", "ابدا من جديد"),
        BotCommand("help", "تعليمات وقوانين البوت")
    ]
    bot.set_my_commands(commands)

# استدعاء إعداد الأوامر عند بدء البوت
set_bot_commands()

# إنشاء اتصال بقاعدة البيانات (مع دعم الخيوط المتعددة)
conn = sqlite3.connect('bot_database.db', check_same_thread=False)

# تنظيف قاعدة البيانات وإضافة الأعمدة اللازمة عند البدء
def clean_database():
    cursor = conn.cursor()
    try:
        # حذف جدول referrals إذا كان موجودًا
        cursor.execute('DROP TABLE IF EXISTS referrals')
    except sqlite3.OperationalError:
        pass

    # إضافة الأعمدة المفقودة إلى جدول users إذا لزم الأمر
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN total_charged INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN total_orders INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_daily_gift TEXT DEFAULT NULL')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN referred_by INTEGER DEFAULT NULL')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN verified_steps TEXT DEFAULT ""')
    except sqlite3.OperationalError:
        pass

    # إزالة referrer_id إذا كان موجودًا، لكن بما أننا نضيف referred_by، نتركه
    conn.commit()

# استدعاء التنظيف عند بدء البوت
clean_database()

# إنشاء الجداول الأخرى إذا لم تكن موجودة
def create_tables():
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0,
        total_charged INTEGER DEFAULT 0,
        total_orders INTEGER DEFAULT 0,
        last_daily_gift TEXT DEFAULT NULL,
        referred_by INTEGER DEFAULT NULL,
        verified_steps TEXT DEFAULT ""
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        name TEXT,
        api_service_id INTEGER,
        price_per_1000 INTEGER,
        min_quantity INTEGER,
        max_quantity INTEGER,
        note TEXT DEFAULT ''
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS codes (
        code TEXT PRIMARY KEY,
        value INTEGER,
        used INTEGER DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS mandatory_channels (
        channel_username TEXT PRIMARY KEY
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS channel_stats (
        channel_username TEXT PRIMARY KEY,
        subscribers_count INTEGER DEFAULT 0,
        points_spent INTEGER DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_subscriptions (
        user_id INTEGER,
        channel_username TEXT,
        PRIMARY KEY (user_id, channel_username)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # إضافة إعداد افتراضي للخدمات المجانية
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('free_services_to_api', '0'))

    # تحديث الجداول لإضافة أعمدة جديدة إذا لم تكن موجودة
    try:
        cursor.execute('ALTER TABLE services ADD COLUMN api_service_id INTEGER')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE services ADD COLUMN note TEXT DEFAULT ""')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE orders ADD COLUMN api_order_id INTEGER DEFAULT NULL')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE channel_stats ADD COLUMN points_spent INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass

    conn.commit()

create_tables()

# متغيرات مؤقتة للتفاعلات
user_states = {}  # لحفظ حالة المستخدم (مثل إضافة خدمة، إلخ)

# جلب حالة الخدمات المجانية
def get_free_services_to_api():
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', ('free_services_to_api',))
    return int(cursor.fetchone()[0])

# فحص الاشتراك في القنوات
def check_subscription(user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT channel_username FROM mandatory_channels')
    channels = cursor.fetchall()
    if not channels:
        return True
    for channel in channels:
        try:
            member = bot.get_chat_member(f'@{channel[0]}', user_id)
            if member.status in ['left', 'kicked']:
                return False
        except:
            return False
    return True

# تحديث إحصائيات القنوات وإضافة نقاط للمستخدمين الجدد فقط
def update_channel_stats(user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT channel_username FROM mandatory_channels')
    channels = cursor.fetchall()
    added_points = 0
    new_subscriptions = 0
    for channel in channels:
        ch_username = channel[0]
        cursor.execute('SELECT * FROM user_subscriptions WHERE user_id = ? AND channel_username = ?', (user_id, ch_username))
        if not cursor.fetchone():
            try:
                member = bot.get_chat_member(f'@{ch_username}', user_id)
                if member.status not in ['left', 'kicked']:
                    cursor.execute('INSERT INTO user_subscriptions (user_id, channel_username) VALUES (?, ?)', (user_id, ch_username))
                    cursor.execute('UPDATE channel_stats SET subscribers_count = subscribers_count + 1, points_spent = points_spent + 2 WHERE channel_username = ?', (ch_username,))
                    added_points += 2
                    new_subscriptions += 1
            except:
                pass
    if new_subscriptions > 0:
        cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (added_points, user_id))
        conn.commit()
        return added_points, new_subscriptions
    return 0, 0

# عرض قنوات الإجباري للمستخدم مع إيموجي حالة الاشتراك
def show_mandatory_channels(message, from_callback=False):
    user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    cursor = conn.cursor()
    cursor.execute('SELECT channel_username FROM mandatory_channels')
    channels = cursor.fetchall()
    if not channels:
        bot.send_message(message.chat.id, "<b>لا توجد قنوات إجبارية حالياً.</b>", parse_mode='HTML')
        start(message)  # إذا لم تكن هناك قنوات، انتقل مباشرة إلى start
        return
    keyboard = InlineKeyboardMarkup()
    for channel in channels:
        ch_username = channel[0]
        try:
            member = bot.get_chat_member(f'@{ch_username}', user_id)
            status_emoji = "✔️" if member.status not in ['left', 'kicked'] else "❌"
        except:
            status_emoji = "❌"
        keyboard.add(InlineKeyboardButton(f"{status_emoji} اشترك في @{ch_username}", url=f"https://t.me/{ch_username}"))
    msg_text = "<b>عذرًا عزيزي 💖، أنت غير مشترك في بعض قنوات البوت🌟\nاشترك الآن واحصل على هدية بسيطة: 2 نقاط مجانية لكل قناة تشترك فيها مع بوت فولو ميديا! 🎁\nهذه النقاط هدية بسيطة لاستخدامك فولو ميديا 😊\n\nاشترك بالقنوات التالية 👇🏻 واضغط على /start</b>"
    if from_callback:
        try:
            bot.edit_message_text(msg_text, message.chat.id, message.id, parse_mode='HTML', reply_markup=keyboard)
        except telebot.apihelper.ApiTelegramException as e:
            if "message is not modified" in str(e):
                pass  # تجاهل الخطأ إذا كان المحتوى نفسه
    else:
        bot.send_message(message.chat.id, msg_text, parse_mode='HTML', reply_markup=keyboard)

# ستارت المستخدمين
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    referred_by = None
    if len(args) > 1:
        try:
            referred_by = int(args[1])
        except ValueError:
            pass

    if user_id == DEVELOPER_ID:
        show_developer_panel(message)
        return
    
    cursor = conn.cursor()
    # Check if user exists
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        # Initialize new user
        cursor.execute('INSERT INTO users (user_id, balance, total_charged, total_orders, referred_by, verified_steps) VALUES (?, 0, 0, 0, ?, "")', (user_id, referred_by))
        conn.commit()
        balance = 0
    else:
        balance = user[0]
        # Update referred_by only if not set
        if referred_by:
            cursor.execute('UPDATE users SET referred_by = ? WHERE user_id = ? AND referred_by IS NULL', (referred_by, user_id))
            conn.commit()
    
    if not check_subscription(user_id):
        show_mandatory_channels(message)
        return
    
    points_added, new_subs = update_channel_stats(user_id)
    if points_added > 0:
        bot.send_message(message.chat.id, f"<b>شكرًا لك على اشتراكك! 🎉\nأنت اشتركت في {new_subs} قناة جديدة وحصلت على {points_added} نقاط هدية! 💎\nرصيدك الآن: {balance + points_added} نقطة.</b>", parse_mode='HTML')
    
    # Refresh balance after potential update
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    balance = cursor.fetchone()[0]
    
    welcome = f"<b>اهلا بك عزيزي في بوت فولو ميديا 👋</b>\n\n💰›رصـيـدك : {balance} نقطة\n⬅️›ايـديـك: {user_id}"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("💼 الخدمات", callback_data="services"))
    keyboard.add(InlineKeyboardButton("تجميع نقاط ⭐", callback_data="collect_points"))
    keyboard.add(
        InlineKeyboardButton("💎 الرصيد", callback_data="balance"),
        InlineKeyboardButton("📝 طلباتي", callback_data="my_orders")
    )
    keyboard.add(
        InlineKeyboardButton("➕ اضف رصيد", callback_data="add_balance"),
        InlineKeyboardButton("🎟️ استخدام كود", callback_data="use_code")
    )
    keyboard.add(
        InlineKeyboardButton("📄 معلومات الطلب", callback_data="order_info"),
        InlineKeyboardButton("👤 الحساب", callback_data="account")
    )
    keyboard.add(
        InlineKeyboardButton("تمويل اجباري 👥", callback_data="mandatory_funding"),
        InlineKeyboardButton("تحويل نقاط ♻️", callback_data="transfer_points")
    )
    keyboard.add(
        InlineKeyboardButton("تمويل اعضاء حقيقي فولو ميديا 👥", callback_data="funding_members")
    )
    keyboard.add(
        InlineKeyboardButton("قناة البوت 📢", url="https://t.me/mediafolo")
    )
    keyboard.add(InlineKeyboardButton("📊 احصائيات البوت", callback_data="bot_stats"))
    bot.send_message(message.chat.id, welcome, parse_mode='HTML', reply_markup=keyboard)

# معالجة أمر المساعدة
@bot.message_handler(commands=['help'])
def help_command(message):
    if not check_subscription(message.from_user.id):
        show_mandatory_channels(message)
        return
    help_message = """
<b>📜 شروط استخدام بوت فولو ميديا</b>

<b>مرحباً بك في بوت فولو ميديا! 💎</b>
بوت عربي مخصّص لتقديم جميع خدمات مواقع التواصل الاجتماعي مثل: <b>إنستغرام، تيك توك، يوتيوب، تويتر، فيسبوك</b> وغيرها من المنصات الشهيرة.
قبل استخدامك للبوت، نرجو قراءة الشروط التالية بعناية 👇

<b>⚙️ الخصوصية والأمان:</b>
الأمان والثقة هما الأساس لدينا 🔐  
جميع بيانات المستخدمين — من نقاط وطلبات — محفوظة بسرّية تامة، ولا يمكن لأي شخص الاطّلاع عليها إلا في حال طلب المستخدم ذلك بنفسه عبر الدعم الفني.

<b>🚫 تنبيهات هامة:</b>
في حال كان الحساب أو القناة التي تطلب الخدمة لها خصوصية مفعّلة (خاصة)، سيتم <b>إلغاء الطلب تلقائياً</b> واسترجاع النقاط إلى رصيدك.  
لذلك، تأكّد دائماً أن الحساب عام قبل الطلب ✅

<b>🆕 تحديث الخدمات:</b>
نقوم بتحديث الخدمات بشكل يومي ✨  
لا توجد خدمات ثابتة، بل تتم إضافة خدمات جديدة باستمرار لتناسب جميع المستخدمين في البوت، ولنبقى دائماً <b>الأول والأفضل</b> 💪

<b>💯 جودة الخدمات:</b>
جميع الخدمات التي يقدمها بوت <b>فولو ميديا</b> موثوقة ومُجرّبة مسبقاً قبل إضافتها للبوت، ولهذا تتوفّر أنواع متعددة من الخدمات بأسعار متفاوتة حسب الجودة والسرعة.

<b>📌 مهم جداً لمتابعين إنستقرام:</b>
إذا كنت تريد إنشاء طلب جديد (متابعين إنستقرام) يجب تعطيل خيار <b>"تمييز للمراجعة"</b>:  
1. انتقل إلى إعدادات الحساب.  
2. اختر خيار "متابعة ودعوة الأصدقاء".  
3. ابحث عن خيار "تمييز للمراجعة" وقم بتعطيله.  
<i>هذا أمر ضروري لضمان إضافة المتابعين الجدد تلقائيًا إلى قائمة متابعيك.</i>

<b>📢 ملاحظة مهمة حول الرشق الثابت:</b>
في حال طلبك رشق تلغرام ثابت، يجب أن يكون لديك <b>رابط دعوة فعّال</b> لقناتك أو مجموعتك العامة.  
📍 <b>الخطوات:</b>  
1. ادخل إلى إعدادات القناة أو المجموعة.  
2. اضغط على ✏️ القلم.  
3. اختر "إنشاء رابط دعوة".  
4. أرسل الرابط عند الطلب في البوت.  
⚠️ لا تقم بتعطيل الرابط بعد الإرسال حتى لا تفقد رصيدك.

<b>📣 قنوات بوت فولو ميديا على تيليجرام:</b>  
القناة الرسمية: <b>@mediafolo</b>  
يتم فيها نشر جميع العروض والتحديثات والمعلومات الخاصة بالبوت.

<b>✍️ فريق بوت فولو ميديا</b>  
نحن دائماً في خدمتكم ❤️
"""
    bot.send_message(message.chat.id, help_message, parse_mode='HTML')

# لوحة المطور
def show_developer_panel(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("اضف خدمة جديدة", callback_data="add_service"),
        InlineKeyboardButton("حذف خدمة", callback_data="delete_service")
    )
    keyboard.add(
        InlineKeyboardButton("انشاء كود فريد", callback_data="create_code"),
        InlineKeyboardButton("تصفير رصيد", callback_data="reset_balance")
    )
    keyboard.add(
        InlineKeyboardButton("فحص طلبات", callback_data="check_orders"),
        InlineKeyboardButton("اضافة قنوات اجباري", callback_data="add_mandatory_channel")
    )
    keyboard.add(
        InlineKeyboardButton("قنوات الاجباري", callback_data="mandatory_channels"),
        InlineKeyboardButton("معلومات القنوات", callback_data="channels_info")
    )
    keyboard.add(
        InlineKeyboardButton("تصفير قناة (مسح بيانات اشتراك)", callback_data="reset_channel"),
        InlineKeyboardButton("جلب ملفات تخزين", callback_data="backup_files")
    )
    keyboard.add(InlineKeyboardButton("الخدمات المجانية", callback_data="toggle_free_services"))
    keyboard.add(InlineKeyboardButton("عرض تمويل البوت", callback_data="view_funding"))
    bot.send_message(message.chat.id, "<b>اهلا بك عزيزي المطور ⚙️👋</b>", parse_mode='HTML', reply_markup=keyboard)

# دالة للتحقق من النشاط ومنح نقاط الدعوة بعد 10 ثواني
def check_and_award_referral(user_id, referred_by):
    if not referred_by:
        return  # No referral, exit early

    cursor = conn.cursor()
    cursor.execute('SELECT verified_steps FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    # Check if user exists and has verified_steps
    if result is None:
        print(f"Error: User {user_id} not found in database.")
        return  # User not found, exit early

    verified_steps = result[0].split(',') if result[0] else []
    
    # Check if both required steps are completed
    if set(['daily_gift', 'services']).issubset(set(verified_steps)):
        def award_points():
            try:
                cursor = conn.cursor()
                # Award 5 points to the new user
                cursor.execute('UPDATE users SET balance = balance + 5 WHERE user_id = ?', (user_id,))
                # Award 50 points to the referrer
                cursor.execute('UPDATE users SET balance = balance + 50 WHERE user_id = ?', (referred_by,))
                conn.commit()
                
                # Notify new user
                bot.send_message(user_id, "<b>شكرا لك! حصلت على 5 نقاط، وحصل صديقك على 50 نقطة.</b>", parse_mode='HTML')
                # Notify referrer
                try:
                    bot.send_message(referred_by, "<b>لقد حصلت على 50 نقطة لدعوتك احد المستخدمين.</b>", parse_mode='HTML')
                except Exception as e:
                    print(f"Failed to notify referrer {referred_by}: {str(e)}")
                
                # Clear verified_steps to prevent re-awarding
                cursor.execute('UPDATE users SET verified_steps = "" WHERE user_id = ?', (user_id,))
                conn.commit()
            except Exception as e:
                print(f"Error awarding referral points: {str(e)}")
        
        # Schedule the awarding of points after 10 seconds
        threading.Timer(10, award_points).start()

# معالجة الضغط على الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    # فحص الاشتراك الإجباري قبل أي تفاعل (إلا لوحة المطور)
    if user_id != DEVELOPER_ID and not check_subscription(user_id):
        show_mandatory_channels(call.message, from_callback=True)
        return

    cursor = conn.cursor()

    if data == "services":
        keyboard = InlineKeyboardMarkup(row_width=2)
        categories = [
            "🎁 خدمات مجانية", "📱 خدمات تلغرام", "📸 خدمات انستغرام",
            "👍 خدمات فيسبوك", "🐦 خدمات تويتر", "🎵 خدمات تيك توك",
            "▶️ خدمات يوتيوب", "🎮 خدمات عروض مميزة", "💬 خدمات واتس اب",
            "👻 خدمات سناب شات", "🌐 خدمات عامة"
        ]

        keyboard.add(InlineKeyboardButton("🎁 خدمات مجانية", callback_data="category_🎁 خدمات مجانية"))
        for i in range(1, len(categories), 2):
            row = [InlineKeyboardButton(categories[i], callback_data=f"category_{categories[i]}")]
            if i + 1 < len(categories):
                row.append(InlineKeyboardButton(categories[i + 1], callback_data=f"category_{categories[i + 1]}"))
            keyboard.add(*row)
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="back_to_start"))

        try:
            bot.edit_message_text(
                "<b>اختر فئة الخدمات:</b>",
                call.message.chat.id,
                call.message.id,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        except telebot.apihelper.ApiTelegramException as e:
            if "message is not modified" in str(e):
                pass

        # إضافة 'services' إلى verified_steps مع التحقق من القيم
        cursor.execute('SELECT verified_steps, referred_by FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            verified_steps = result[0].split(',') if result[0] else []
            referred_by = result[1]
            if 'services' not in verified_steps:
                verified_steps.append('services')
                cursor.execute('UPDATE users SET verified_steps = ? WHERE user_id = ?', (','.join(verified_steps), user_id))
                conn.commit()
                check_and_award_referral(user_id, referred_by)
        else:
            print(f"⚠️ المستخدم {user_id} غير موجود في قاعدة البيانات!")

    elif data.startswith("category_"):
        category = data.split("category_")[1]
        cursor.execute('SELECT id, name FROM services WHERE category = ?', (category,))
        services = cursor.fetchall()
        keyboard = InlineKeyboardMarkup(row_width=2)
        for service in services:
            keyboard.add(InlineKeyboardButton(service[1], callback_data=f"service_id_{service[0]}"))
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="services"))
        try:
            bot.edit_message_text(
                f"<b>خدمات {category}:</b>",
                call.message.chat.id,
                call.message.id,
                parse_mode='HTML',
                reply_markup=keyboard
            )
        except telebot.apihelper.ApiTelegramException as e:
            if "message is not modified" in str(e):
                pass

    elif data.startswith("service_id_"):
        service_id = data.split("service_id_")[1]
        cursor.execute('SELECT name, price_per_1000, min_quantity, max_quantity, note, category FROM services WHERE id = ?', (service_id,))
        details = cursor.fetchone()
        if details:
            service_name, price, min_q, max_q, note, category = details
            msg = (
                f"<b>{service_name}</b>\n\n"
                f"السعر: {price} نقطة لكل 1000\n"
                f"اقل طلب: {min_q}\n"
                f"اكبر طلب: {max_q}\n\n"
                f"ملاحظة: {note}\n\n"
                "ارسل الكمية التي تريدها:"
            )
            user_states[user_id] = {
                'state': 'quantity',
                'service': service_name,
                'service_id': service_id,
                'price': price,
                'min': min_q,
                'max': max_q,
                'category': category
            }
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data=f"category_{category}"))
            bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)

    elif data == "balance":
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        balance = result[0] if result else 0
        try:
            bot.answer_callback_query(call.id, f"رصيدك الحالي: {balance} نقطة 💰", show_alert=True)
        except telebot.apihelper.ApiTelegramException as e:
            if "query is too old" in str(e):
                pass

    elif data == "my_orders":
        cursor.execute('SELECT order_id, service_name, status FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 5', (user_id,))
        orders = cursor.fetchall()
        msg = "<b>آخر 5 طلبات 💼:</b>\n"
        if orders:
            for order in orders:
                msg += f"ID: {order[0]} - {order[1]} - حالة: {order[2]}\n"
        else:
            msg += "ما في طلبات بعد 🙁"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="back_to_start"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "add_balance":
        msg = """
<b>نـقـاط بـوت فـولـو مـيـديـا 💎</b>
<b>أسـعـار الـنقـاط 💳</b>
💵 <b>$1</b> → 1,000 نقطة
💵 <b>$2</b> → 2,000 نقطة
💵 <b>$3</b> → 3,000 نقطة
💵 <b>$4</b> → 4,000 نقطة
💵 <b>$5</b> → 5,000 نقطة
💰 <b>$10</b> → 10,000 نقطة
💰 <b>$20</b> → 20,000 نقطة
💰 <b>$50</b> → 50,000 نقطة
💎 <b>$150</b> → 150,000 نقطة

<b>⚡ استخدم نقاطك للاستمتاع بالخدمات المميزة والفريدة من فولو ميديا</b>
<b>لشراء النقاط، تواصل مع حساب الدعم الرسمي:</b>
"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("دعم فولو ميديا", url="https://t.me/Helpfolo"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "use_code":
        user_states[user_id] = {'state': 'use_code'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_start"))
        bot.edit_message_text("<b>ارسل الكود الآن 🔑:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "bot_stats":
        cursor.execute('SELECT COUNT(*) FROM users')
        users_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM orders')
        orders_count = cursor.fetchone()[0]
        msg = f"<b>احصائيات بوت فولو ميديا 📊:</b>\nعدد المستخدمين: {users_count}\nعدد الطلبات: {orders_count}"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_start"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "order_info":
        user_states[user_id] = {'state': 'order_info'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_start"))
        bot.edit_message_text("<b>ارسل ID الطلب لتتبعه 🔍:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "account":
        cursor.execute('SELECT balance, total_charged, total_orders FROM users WHERE user_id = ?', (user_id,))
        info = cursor.fetchone()
        msg = f"<b>معلومات حسابك 👤:</b>\nرصيد حالي: {info[0]} نقطة\nإجمالي الشحن: {info[1]} نقطة\nإجمالي الطلبات: {info[2]}"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_start"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "mandatory_funding":
        msg = """
<b>اهلا بك في قسم تمويل بوت فولو ميديا 👥</b>

<b>تمويل البوت مختلف وجديد كليًا! 🔥</b>
التمويل لدينا حقيقي 100%، وهو عبارة عن اشتراك اجباري في البوت. تستطيع شراء وطلب تمويل من المطور مقابل نقاط أو دولارات ($).

<b>تفاصيل التمويل:</b>
- كل 1 عضو سعره: <b>10 نقاط</b> 💎
- أقل طلب يمكن تمويله: <b>100 عضو</b> 👥

<b>بإمكانك تجميع النقاط من خلال:</b>
- رابط الدعوة 🔗
- الهدية اليومية 🎁
- الشحن بواسطة حساب الدعم الرسمي ☺️

<b>تواصل مع الدعم للحصول على تمويلك الآن!</b>
"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("حساب الدعم الرسمي", url="https://t.me/Helpfolo"))
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="back_to_start"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "collect_points":
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("الهدية اليومية 🎁", callback_data="daily_gift"),
            InlineKeyboardButton("رابط الدعوة 🔗", callback_data="referral_link")
        )
        keyboard.add(InlineKeyboardButton("الانضمام بلقنوات", callback_data="join_channels"))
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="back_to_start"))
        bot.edit_message_text("<b>قسم تجميع النقاط ⭐:</b>\nاختر خيارًا لتجميع نقاطك مجانًا!", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "daily_gift":
        cursor = conn.cursor()
        cursor.execute('SELECT last_daily_gift, verified_steps, referred_by FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        last_gift, verified_steps_str, referred_by = result
        verified_steps = verified_steps_str.split(',') if verified_steps_str else []
        now = datetime.now()
        if last_gift:
            last_gift_time = datetime.fromisoformat(last_gift)
            if now - last_gift_time < timedelta(hours=24):
                time_left = (last_gift_time + timedelta(hours=24) - now).seconds
                hours_left = time_left // 3600
                minutes_left = (time_left % 3600) // 60
                try:
                    bot.answer_callback_query(call.id, f"لقد حصلت على هديتك اليومية بالفعل! أعد المحاولة بعد {hours_left} ساعات و{minutes_left} دقائق. ⏳", show_alert=True)
                except telebot.apihelper.ApiTelegramException as e:
                    if "query is too old" in str(e):
                        pass
                return
        # أعطِ 20 نقطة
        cursor.execute('UPDATE users SET balance = balance + 20, last_daily_gift = ? WHERE user_id = ?', (now.isoformat(), user_id))
        conn.commit()
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        new_balance = cursor.fetchone()[0]
        try:
            bot.answer_callback_query(call.id, f"تهانينا! 🎉\nلقد حصلت على 20 نقطة هدية يومية! 💎\nرصيدك الآن: {new_balance} نقطة.", show_alert=True)
        except telebot.apihelper.ApiTelegramException as e:
            if "query is too old" in str(e):
                pass

        # إضافة 'daily_gift' إلى verified_steps
        if 'daily_gift' not in verified_steps:
            verified_steps.append('daily_gift')
            cursor.execute('UPDATE users SET verified_steps = ? WHERE user_id = ?', (','.join(verified_steps), user_id))
            conn.commit()
            check_and_award_referral(user_id, referred_by)
    
    elif data == "referral_link":
        referral_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        msg = f"<b>رابط الدعوة الخاص بك 🔗:</b>\n\n{referral_link}\n\n<b>شارك الرابط مع أصدقائك! لكل مستخدم جديد يدخل عبر رابطك:</b>\n- تحصل أنت على <b>50 نقطة</b> 💎\n- يحصل المدعو على <b>5 نقاط</b> هدية! 🎁\n\nدع أصدقاءك واكسب نقاطًا مجانًا!"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="collect_points"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "transfer_points":
        user_states[user_id] = {'state': 'transfer_id'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="back_to_start"))
        bot.edit_message_text("<b>أرسل ID الشخص الذي تريد تحويل النقاط إليه 🔢:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "funding_members":
        msg = """
<b>اهلا بك في قسم تمويل الأعضاء الحقيقيين في فولو ميديا 👥</b>

<b>تفاصيل التمويل:</b>
- سعر كل عضو: <b>8 نقاط</b> 💎
- الأعضاء حقيقيون 100% من مستخدمي البوت الذين يجمعون النقاط.
- للتمويل، رفع البوت مشرفًا في قناتك أو مجموعتك مع صلاحيات دعوة المستخدمين.
- القناة أو المجموعة يجب أن تكون عامة برابط عام (@username).
- أقل تمويل: 40 عضو.

<b>ملاحظة هامة:</b> لا تقم بإزالة البوت من المشرفين قبل انتهاء التمويل، وإلا سيتم إلغاء التمويل وخصم النقاط.

<b>ابدأ تمويلك الآن!</b>
"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("اضف تمويلك الان 👥", callback_data="add_funding"))
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="back_to_start"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)

    elif data == "add_funding":
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        balance = cursor.fetchone()[0]
        max_members = balance // 8
        min_members = 40
        if max_members < min_members:
            bot.answer_callback_query(call.id, "نقاطك غير كافية لتمويل أقل عدد (40 عضو). جمع نقاط أكثر! ⚠️", show_alert=True)
            return
        user_states[user_id] = {'state': 'funding_quantity', 'max_members': max_members}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="funding_members"))
        bot.edit_message_text(f"<b>نقاطك: {balance} 💎\nأقصى عدد يمكن تمويله: {max_members} عضو\nأرسل العدد المطلوب (أقل {min_members}):</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)

    elif data == "join_channels":
        msg = """
<b>اهلا بك في قسم الانضمام إلى القنوات لتجميع النقاط ⭐</b>

<b>تفاصيل:</b>
- لكل اشتراك في قناة أو مجموعة، احصل على <b>5 نقاط</b> مجانًا 💎.
- القنوات المعروضة هي تلك التي لم تنضم إليها مؤخرًا (أكثر من أسبوع).
- اشترك، تحقق، واحصل على نقاطك فورًا!

<b>ابدأ الآن واجمع نقاطك!</b>
"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("ابدا الان بتجميع النقاط ⚡", callback_data="start_joining"))
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="collect_points"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)

    elif data == "start_joining":
        channel = get_next_channel_for_user(user_id)
        if not channel:
            bot.edit_message_text("<b>لا توجد قنوات متاحة الآن. أعد المحاولة لاحقًا! ⏳</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
            return
        msg = f"<b>اشترك في @{channel['username']} واحصل على 5 نقاط! 👥</b>"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("اضغط لاشتراك 📢", url=f"https://t.me/{channel['username']}"))
        keyboard.add(
            InlineKeyboardButton("التالي (تحقق الاشتراك) 🔍", callback_data=f"check_join_{channel['id']}"),
            InlineKeyboardButton("تخطي ➡️", callback_data="skip_channel")
        )
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="join_channels"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)

    elif data.startswith("check_join_"):
        channel_id = int(data.split("_")[2])
        awarded = check_and_award_join(user_id, channel_id)
        if awarded:
            bot.answer_callback_query(call.id, "احسنت! تم إضافة 5 نقاط إلى رصيدك ✅", show_alert=True)
            bot.edit_message_text("<b>تم التحقق بنجاح! 🎉\nجاري عرض قناة جديدة...</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
            time.sleep(1)
            callback_handler(call)  # إعادة عرض قناة جديدة
        else:
            bot.answer_callback_query(call.id, "أنت غير مشترك في القناة. اشترك أولاً ثم أعد المحاولة! ⚠️", show_alert=True)

    elif data == "skip_channel":
        bot.edit_message_text("<b>تم التخطي! جاري عرض قناة جديدة...</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
        time.sleep(1)
        callback_handler(call)  # عرض قناة جديدة

    elif data == "back_to_start":
        bot.delete_message(call.message.chat.id, call.message.id)
        start(call.message)
    
    elif data == "confirm_link_yes":
        if user_id in user_states and 'link' in user_states[user_id]:
            captcha_code = random.randint(100, 999)
            user_states[user_id]['captcha_code'] = captcha_code
            user_states[user_id]['state'] = 'captcha'
            bot.edit_message_text(f"<b>للتحقق، أدخل الرقم التالي: {captcha_code}</b>", call.message.chat.id, call.message.id, parse_mode='HTML')

    elif data == "confirm_link_no":
        bot.edit_message_text("<b>حسنا، تم الإلغاء ❌.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
        if user_id in user_states:
            del user_states[user_id]
        start(call.message)  # إعادة عرض قائمة البداية

    elif data == "confirm_transfer_yes":
        if user_id in user_states and 'amount' in user_states[user_id]:
            captcha_code = random.randint(100, 999)
            user_states[user_id]['captcha_code'] = captcha_code
            user_states[user_id]['state'] = 'transfer_captcha'
            bot.edit_message_text(f"<b>للتحقق النهائي، أدخل الرقم: {captcha_code} 🔒</b>", call.message.chat.id, call.message.id, parse_mode='HTML')

    elif data == "confirm_transfer_no":
        bot.edit_message_text("<b>تم إلغاء التحويل ❌.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
        if user_id in user_states:
            del user_states[user_id]
        start(call.message)

    elif data == "confirm_funding_yes":
        if user_id in user_states and 'channel_username' in user_states[user_id]:
            channel_username = user_states[user_id]['channel_username']
            quantity = user_states[user_id]['quantity']
            result = add_funding_request(user_id, channel_username, quantity)
            if result == "added":
                bot.edit_message_text("<b>تم إضافة التمويل بنجاح ✅! سيبدأ جذب الأعضاء قريباً.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
            elif result == "queue":
                bot.edit_message_text("<b>تم إضافتك إلى طابور الانتظار ⏳. سنخطرك عند الإضافة.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
            del user_states[user_id]
            start(call.message)

    elif data == "confirm_funding_no":
        bot.edit_message_text("<b>تم إلغاء التمويل ❌.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
        if user_id in user_states:
            del user_states[user_id]
        start(call.message)
        
# تأكيد الطلب من المجموعة
    elif data.startswith("confirm_order_"):
        order_id = data.split("confirm_order_")[1]
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = "تم التنفيذ" WHERE order_id = ?', (order_id,))
        conn.commit()
        bot.edit_message_text(call.message.text + "\n\n<b>تم التنفيذ ✅</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
        try:
            bot.answer_callback_query(call.id, "تم تغيير الحالة إلى تم التنفيذ.", show_alert=True)
        except telebot.apihelper.ApiTelegramException as e:
            if "query is too old" in str(e):
                pass
    
    elif data.startswith("cancel_order_"):
        order_id = data.split("cancel_order_")[1]
        bot.edit_message_text(call.message.text + "\n\n<b>تم الإلغاء ❌</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
        try:
            bot.answer_callback_query(call.id, "تم إلغاء الطلب.", show_alert=True)
        except telebot.apihelper.ApiTelegramException as e:
            if "query is too old" in str(e):
                pass
    
    # لوحة المطور
    if user_id != DEVELOPER_ID:
        return
    
    if data == "add_service":
        keyboard = InlineKeyboardMarkup(row_width=2)
        categories = ["🎁 خدمات مجانية", "📱 خدمات تلغرام", "📸 خدمات انستغرام", "👍 خدمات فيسبوك", "🐦 خدمات تويتر", "🎵 خدمات تيك توك", "▶️ خدمات يوتيوب", "🎮 خدمات عروض مميزة", "💬 خدمات واتس اب", "👻 خدمات سناب شات", "🌐 خدمات عامة"]
        for i in range(0, len(categories), 2):
            row = [InlineKeyboardButton(categories[i], callback_data=f"add_cat_{categories[i]}")]
            if i + 1 < len(categories):
                row.append(InlineKeyboardButton(categories[i + 1], callback_data=f"add_cat_{categories[i + 1]}"))
            keyboard.add(*row)
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>اختر فئة الخدمة الجديدة 🛠️:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("add_cat_"):
        category = data.split("add_cat_")[1]
        user_states[user_id] = {'state': 'add_service_name', 'category': category}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="add_service"))
        bot.edit_message_text("<b>ارسل اسم الزر الجديد للخدمة (مثل: شحن نجوم تلغرام) 📝:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "delete_service":
        keyboard = InlineKeyboardMarkup(row_width=2)
        categories = ["🎁 خدمات مجانية", "📱 خدمات تلغرام", "📸 خدمات انستغرام", "👍 خدمات فيسبوك", "🐦 خدمات تويتر", "🎵 خدمات تيك توك", "▶️ خدمات يوتيوب", "🎮 خدمات عروض مميزة", "💬 خدمات واتس اب", "👻 خدمات سناب شات", "🌐 خدمات عامة"]
        for i in range(0, len(categories), 2):
            row = [InlineKeyboardButton(categories[i], callback_data=f"del_cat_{categories[i]}")]
            if i + 1 < len(categories):
                row.append(InlineKeyboardButton(categories[i + 1], callback_data=f"del_cat_{categories[i + 1]}"))
            keyboard.add(*row)
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>اختر فئة الخدمة لحذفها 🗑️:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("del_cat_"):
        category = data.split("del_cat_")[1]
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM services WHERE category = ?', (category,))
        services = cursor.fetchall()
        keyboard = InlineKeyboardMarkup(row_width=2)
        for service in services:
            keyboard.add(InlineKeyboardButton(service[1], callback_data=f"del_service_{service[0]}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="delete_service"))
        bot.edit_message_text(f"<b>خدمات {category} لحذفها:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("del_service_"):
        service_id = int(data.split("del_service_")[1])
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM services WHERE id = ?', (service_id,))
        service_name = cursor.fetchone()[0]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("نعم", callback_data=f"confirm_del_service_{service_id}"),
            InlineKeyboardButton("لا", callback_data="delete_service")
        )
        bot.edit_message_text(f"<b>هل ترغب بحذف الخدمة '{service_name}' نهائياً ❓</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("confirm_del_service_"):
        service_id = int(data.split("confirm_del_service_")[1])
        cursor = conn.cursor()
        cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
        conn.commit()
        bot.edit_message_text("<b>تم حذف الخدمة بنجاح ✅.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "create_code":
        user_states[user_id] = {'state': 'create_code_value'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل عدد النقاط التي تريد إضافتها (مثل: 1000) 💵:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "reset_balance":
        user_states[user_id] = {'state': 'reset_user_id'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل ID الشخص 🔢:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "check_orders":
        user_states[user_id] = {'state': 'check_order_id'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل ID الطلب لفحصه 🔍:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "add_mandatory_channel":
        user_states[user_id] = {'state': 'add_channel'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل يوزر القناة (بدون @) 📢:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "mandatory_channels":
        cursor = conn.cursor()
        cursor.execute('SELECT channel_username FROM mandatory_channels')
        channels = cursor.fetchall()
        keyboard = InlineKeyboardMarkup()
        for channel in channels:
            keyboard.add(InlineKeyboardButton(f"@{channel[0]}", callback_data=f"delete_channel_{channel[0]}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>قنوات الإجباري 📋:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("delete_channel_"):
        channel = data.split("delete_channel_")[1]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("نعم", callback_data=f"confirm_delete_{channel}"),
            InlineKeyboardButton("لا", callback_data="mandatory_channels")
        )
        bot.edit_message_text(f"<b>هل ترغب بحذف @{channel} من الإجباري ❓</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("confirm_delete_"):
        channel = data.split("confirm_delete_")[1]
        cursor = conn.cursor()
        cursor.execute('DELETE FROM mandatory_channels WHERE channel_username = ?', (channel,))
        cursor.execute('DELETE FROM channel_stats WHERE channel_username = ?', (channel,))
        cursor.execute('DELETE FROM user_subscriptions WHERE channel_username = ?', (channel,))
        conn.commit()
        bot.edit_message_text("<b>تم الحذف بنجاح ✅. (تم مسح بيانات الاشتراكات لهذه القناة أيضًا)</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "channels_info":
        cursor = conn.cursor()
        cursor.execute('SELECT channel_username, subscribers_count, points_spent FROM channel_stats')
        stats = cursor.fetchall()
        msg = "<b>معلومات القنوات 📈:</b>\n"
        for stat in stats:
            msg += f"@{stat[0]} - مشتركين عبر البوت: {stat[1]} - نقاط مصروفة: {stat[2]}\n"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "reset_channel":
        cursor = conn.cursor()
        cursor.execute('SELECT channel_username FROM mandatory_channels')
        channels = cursor.fetchall()
        keyboard = InlineKeyboardMarkup()
        for channel in channels:
            keyboard.add(InlineKeyboardButton(f"@{channel[0]}", callback_data=f"reset_channel_confirm_{channel[0]}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>اختر قناة لتصفير بيانات اشتراكها (سيتم مسح الاشتراكات السابقة لها فقط، دون حذفها من الإجباري) 🧹:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("reset_channel_confirm_"):
        channel = data.split("reset_channel_confirm_")[1]
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_subscriptions WHERE channel_username = ?', (channel,))
        cursor.execute('UPDATE channel_stats SET subscribers_count = 0, points_spent = 0 WHERE channel_username = ?', (channel,))
        conn.commit()
        bot.edit_message_text(f"<b>تم تصفير بيانات @{channel} بنجاح ✅. الآن إذا أعاد المستخدمون الاشتراك، سيحصلون على نقاط جديدة.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "toggle_free_services":
        current_state = get_free_services_to_api()
        new_state = 1 - current_state  # تبديل 0/1
        cursor = conn.cursor()
        cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (str(new_state), 'free_services_to_api'))
        conn.commit()
        state_text = "مفعلة (ترسل إلى API)" if new_state == 1 else "معطلة (ترسل إلى المجموعة فقط)"
        try:
            bot.answer_callback_query(call.id, f"تم تغيير حالة الخدمات المجانية إلى: {state_text} ✅", show_alert=True)
        except telebot.apihelper.ApiTelegramException as e:
            if "query is too old" in str(e):
                pass
    
    elif data == "backup_files":
        send_backup()
        try:
            bot.answer_callback_query(call.id, "تم إرسال الملفات 📂.", show_alert=True)
        except telebot.apihelper.ApiTelegramException as e:
            if "query is too old" in str(e):
                pass

    elif data == "view_funding":
        fundings = get_active_fundings()
        keyboard = InlineKeyboardMarkup()
        for funding in fundings:
            keyboard.add(InlineKeyboardButton(f"@{funding['channel_username']}", callback_data=f"funding_details_{funding['id']}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        msg = "<b>قائمة التمويلات النشطة 👥:</b>" if fundings else "<b>لا توجد تمويلات نشطة حاليًا.</b>"
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)

    elif data.startswith("funding_details_"):
        funding_id = int(data.split("_")[2])
        details = get_funding_details(funding_id)
        if details:
            msg = f"<b>تفاصيل التمويل لـ @{details['channel_username']}:</b>\nعدد المطلوب: {details['requested_members']}\nعدد المتبقي: {details['remaining_members']}\nمستخدم: {details['user_id']}"
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("حذف التمويل 🗑️", callback_data=f"confirm_remove_funding_{funding_id}"))
            keyboard.add(InlineKeyboardButton("رجوع", callback_data="view_funding"))
            bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)

    elif data.startswith("confirm_remove_funding_"):
        funding_id = int(data.split("_")[3])
        removed = remove_funding(funding_id)
        if removed:
            bot.edit_message_text("<b>تم حذف التمويل بنجاح ✅. تم إخطار المستخدم.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')

    elif data == "dev_back":
        bot.delete_message(call.message.chat.id, call.message.id)
        show_developer_panel(call.message)
    
    elif data.startswith("confirm_reset_"):
        parts = data.split("_")
        target_id = int(parts[2])
        amount = int(parts[3])
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (amount, target_id))
        conn.commit()
        bot.edit_message_text("<b>تم الخصم بنجاح ✅.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
# معالجة الرسائل النصية (للإدخالات)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text
    
    if user_id in user_states:
        state = user_states[user_id].get('state')
        
        if state == 'quantity':
            try:
                quantity = int(text)
                service = user_states[user_id]['service']
                min_q = user_states[user_id]['min']
                max_q = user_states[user_id]['max']
                if quantity < min_q or quantity > max_q:
                    bot.reply_to(message, f"<b>الكمية يجب أن تكون بين {min_q} و {max_q} ⚠️.</b>", parse_mode='HTML')
                    return
                user_states[user_id]['quantity'] = quantity
                user_states[user_id]['state'] = 'link'
                bot.reply_to(message, "<b>ارسل الرابط الذي تريد الخدمة إليه 🔗:</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل رقم صحيح ❌.</b>", parse_mode='HTML')
        
        elif state == 'link':
            link = text
            user_states[user_id]['link'] = link
            msg = f"<b>الرابط الذي أرسلته: {link}\nهل أنت متأكد ❓</b>"
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton("نعم", callback_data="confirm_link_yes"),
                InlineKeyboardButton("لا", callback_data="confirm_link_no")
            )
            bot.reply_to(message, msg, parse_mode='HTML', reply_markup=keyboard)
        
        elif state == 'captcha':
            if int(text) == user_states[user_id]['captcha_code']:
                link = user_states[user_id]['link']
                service = user_states[user_id]['service']
                quantity = user_states[user_id]['quantity']
                category = user_states[user_id]['category']
                cursor = conn.cursor()
                cursor.execute('SELECT price_per_1000, api_service_id FROM services WHERE name = ?', (service,))
                result = cursor.fetchone()
                if result is None:
                    bot.reply_to(message, "<b>خطأ: الخدمة غير موجودة.</b>", parse_mode='HTML')
                    del user_states[user_id]
                    start(message)
                    return
                price_per_1000, api_service_id = result
                total_price = (quantity / 1000) * price_per_1000
                
                cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
                balance = cursor.fetchone()[0]
                if balance < total_price:
                    bot.reply_to(message, "<b>رصيدك غير كافي ⚠️.</b>", parse_mode='HTML')
                    del user_states[user_id]
                    start(message)
                    return
                
                # خصم الرصيد
                new_balance = balance - total_price
                cursor.execute('UPDATE users SET balance = ?, total_orders = total_orders + 1 WHERE user_id = ?', (new_balance, user_id))
                conn.commit()
                
                api_response = {}
                api_order_id = None
                free_to_api = get_free_services_to_api()
                if "مجانية" in category and free_to_api == 0:
                    cursor.execute('INSERT INTO orders (user_id, service_name, quantity, link, price) VALUES (?, ?, ?, ?, ?)', (user_id, service, quantity, link, total_price))
                    order_id = cursor.lastrowid
                    conn.commit()
                    
                    msg = f"<b>تم تنفيذ طلبك بنجاح ✅!</b>\nID الطلب: {order_id}\nالسعر: {total_price} نقطة\nتبقى من رصيدك: {new_balance} نقطة\n\nإذا واجهت تأخيرًا في الطلب، تواصل مع الدعم. شكرًا لاستخدامك بوت فولو ميديا! 😊"
                    bot.send_message(message.chat.id, msg, parse_mode='HTML')
                    
                    # إرسال إلى المجموعة بدون API
                    user_info = bot.get_chat(user_id)
                    username = user_info.username if user_info.username else "لا يوجد"
                    group_msg = f"<b>طلب جديد 💼 (مجاني - تنفيذ يدوي):</b>\nID: {order_id}\nمستخدم: {user_id} (@{username})\nخدمة: {service}\nكمية: {quantity}\nرابط: {link}\nسعر: {total_price} نقطة"
                    bot.send_message(GROUP_ID, group_msg, parse_mode='HTML')
                else:
                    api_response = api_handler.add_order(api_service_id, link, quantity)
                    
                    if 'order' in api_response:
                        api_order_id = api_response['order']
                        cursor.execute('INSERT INTO orders (user_id, service_name, quantity, link, price, api_order_id) VALUES (?, ?, ?, ?, ?, ?)', (user_id, service, quantity, link, total_price, api_order_id))
                        order_id = cursor.lastrowid
                        conn.commit()
                        
                        msg = f"<b>تم تنفيذ طلبك بنجاح ✅!</b>\nID الطلب: {order_id}\nالسعر: {total_price} نقطة\nتبقى من رصيدك: {new_balance} نقطة\n\nإذا واجهت تأخيرًا في الطلب، تواصل مع الدعم. شكرًا لاستخدامك بوت فولو ميديا! 😊"
                        bot.send_message(message.chat.id, msg, parse_mode='HTML')
                        
                        # إرسال رد الـ API إلى المجموعة
                        user_info = bot.get_chat(user_id)
                        username = user_info.username if user_info.username else "لا يوجد"
                        group_msg = f"<b>طلب جديد 💼:</b>\nID: {order_id}\nمستخدم: {user_id} (@{username})\nخدمة: {service}\nكمية: {quantity}\nرابط: {link}\nسعر: {total_price} نقطة\n\n<b>رد الـ API:</b> {api_response}"
                        bot.send_message(GROUP_ID, group_msg, parse_mode='HTML')
                    else:
                        # في حال خطأ من الـ API
                        error_msg = api_response.get('error', 'خطأ غير معروف')
                        if error_msg == 'neworder.error.link_duplicate':
                            user_msg = "<b>لديك طلب لم ينتهي بعد على هذا الرابط.</b>"
                        elif 'balance' in error_msg.lower() or 'insufficient' in error_msg.lower():
                            user_msg = "<b>رصيدك غير كافي ⚠️.</b>"
                        else:
                            user_msg = "<b>أوبس، يبدو أن هناك خطأ. فشلت العملية، انتظر قليلاً وأعد المحاولة في وقت آخر.</b>"
                            keyboard = InlineKeyboardMarkup()
                            keyboard.add(InlineKeyboardButton("قناة البوت 👀", url="https://t.me/mediafolo"))
                            bot.send_message(message.chat.id, user_msg, parse_mode='HTML', reply_markup=keyboard)
                            user_msg = ""
                        
                        if user_msg:
                            bot.send_message(message.chat.id, user_msg, parse_mode='HTML')
                        
                        # إرسال الخطأ إلى المجموعة
                        user_info = bot.get_chat(user_id)
                        username = user_info.username if user_info.username else "لا يوجد"
                        group_msg = f"<b>طلب جديد 💼 (خطأ):</b>\nمستخدم: {user_id} (@{username})\nخدمة: {service}\nكمية: {quantity}\nرابط: {link}\n\n<b>رد الـ API:</b> {api_response}"
                        bot.send_message(GROUP_ID, group_msg, parse_mode='HTML')
                
                bot.send_message(message.chat.id, "<b>شكرا لاستخدامك بوت فولو ميديا ☺️</b>", parse_mode='HTML')
                del user_states[user_id]
                start(message)  # إعادة عرض قائمة البداية بعد التنفيذ
            else:
                bot.send_message(message.chat.id, "<b>رمز خاطئ، تم إلغاء الطلب. أعد المحاولة من جديد.</b>", parse_mode='HTML')
                del user_states[user_id]
                start(message)  # إعادة عرض قائمة البداية بعد الإلغاء
        
        elif state == 'use_code':
            code = text.upper()
            cursor = conn.cursor()
            cursor.execute('SELECT value, used FROM codes WHERE code = ?', (code,))
            code_info = cursor.fetchone()
            if code_info and code_info[1] == 0:
                value = code_info[0]
                cursor.execute('UPDATE users SET balance = balance + ?, total_charged = total_charged + ? WHERE user_id = ?', (value, value, user_id))
                cursor.execute('UPDATE codes SET used = 1 WHERE code = ?', (code,))
                conn.commit()
                bot.reply_to(message, f"<b>تم إضافة {value} نقطة إلى رصيدك بنجاح ✅!</b>", parse_mode='HTML')
            else:
                bot.reply_to(message, "<b>هذا الكود غير صالح أو مستخدم ❌.</b>", parse_mode='HTML')
            del user_states[user_id]
            start(message)
        
        elif state == 'order_info':
            try:
                order_id = int(text)
                cursor = conn.cursor()
                cursor.execute('SELECT service_name, quantity, link, price, status FROM orders WHERE order_id = ? AND user_id = ?', (order_id, user_id))
                order = cursor.fetchone()
                if order:
                    msg = f"<b>معلومات الطلب {order_id} 🔍:</b>\nخدمة: {order[0]}\nكمية: {order[1]}\nرابط: {order[2]}\nسعر: {order[3]} نقطة\nحالة: {order[4]}"
                    bot.reply_to(message, msg, parse_mode='HTML')
                else:
                    bot.reply_to(message, "<b>طلب غير موجود ❌.</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل ID صحيح ❌.</b>", parse_mode='HTML')
            del user_states[user_id]
            start(message)
        
        elif state == 'check_order_id' and user_id == DEVELOPER_ID:
            try:
                order_id = int(text)
                cursor = conn.cursor()
                cursor.execute('SELECT user_id, service_name, quantity, link, price, status, api_order_id FROM orders WHERE order_id = ?', (order_id,))
                order = cursor.fetchone()
                if order:
                    api_id_str = f"\nرقم الطلب في الموقع: {order[6]}" if order[6] else ""
                    msg = f"<b>معلومات الطلب {order_id} 🔍:</b>\nمستخدم: {order[0]}\nخدمة: {order[1]}\nكمية: {order[2]}\nرابط: {order[3]}\nسعر: {order[4]} نقطة{api_id_str}\nحالة: {order[5]}"
                    bot.reply_to(message, msg, parse_mode='HTML')
                else:
                    bot.reply_to(message, "<b>طلب غير موجود ❌.</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل ID صحيح ❌.</b>", parse_mode='HTML')
            del user_states[user_id]
        
        # حالات المطور
        elif state == 'add_service_name' and user_id == DEVELOPER_ID:
            name = text
            user_states[user_id] = {'state': 'add_api_service_id', 'category': user_states[user_id]['category'], 'name': name}
            bot.reply_to(message, "<b>ارسل رقم الخدمة التعريفي من الموقع (service ID):</b>", parse_mode='HTML')
        
        elif state == 'add_api_service_id' and user_id == DEVELOPER_ID:
            try:
                api_service_id = int(text)
                user_states[user_id]['api_service_id'] = api_service_id
                user_states[user_id]['state'] = 'add_price'
                bot.reply_to(message, "<b>تم الحفظ ✅. ارسل السعر لكل 1000 (مثل: 100) 💲:</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل رقم صحيح ❌.</b>", parse_mode='HTML')
        
        elif state == 'add_price':
            try:
                price = int(text)
                user_states[user_id]['price'] = price
                user_states[user_id]['state'] = 'add_min'
                bot.reply_to(message, "<b>تم الحفظ ✅. ارسل أقل طلب:</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل رقم ❌.</b>", parse_mode='HTML')
        
        elif state == 'add_min':
            try:
                min_q = int(text)
                user_states[user_id]['min'] = min_q
                user_states[user_id]['state'] = 'add_max'
                bot.reply_to(message, "<b>تم الحفظ ✅. ارسل أكبر طلب:</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل رقم ❌.</b>", parse_mode='HTML')
        
        elif state == 'add_max':
            try:
                max_q = int(text)
                user_states[user_id]['max'] = max_q
                user_states[user_id]['state'] = 'add_note'
                bot.reply_to(message, "<b>تم الحفظ ✅. ارسل ملاحظة للخدمة (مثل: الرجاء ارسال رابط حسابك الخاص فقط):</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل رقم ❌.</b>", parse_mode='HTML')
        
        elif state == 'add_note':
            note = text
            category = user_states[user_id]['category']
            name = user_states[user_id]['name']
            api_service_id = user_states[user_id]['api_service_id']
            price = user_states[user_id]['price']
            min_q = user_states[user_id]['min']
            max_q = user_states[user_id]['max']
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO services (category, name, api_service_id, price_per_1000, min_quantity, max_quantity, note) VALUES (?, ?, ?, ?, ?, ?, ?)', (category, name, api_service_id, price, min_q, max_q, note))
                conn.commit()
                bot.reply_to(message, f"<b>تم إضافة الخدمة '{name}' بنجاح ✅!</b>", parse_mode='HTML')
            except Exception as e:
                bot.reply_to(message, f"<b>خطأ أثناء إضافة الخدمة: {str(e)} ❌</b>", parse_mode='HTML')
            del user_states[user_id]
        
        elif state == 'create_code_value':
            try:
                value = int(text)
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(4,6)))
                cursor = conn.cursor()
                cursor.execute('INSERT INTO codes (code, value) VALUES (?, ?)', (code, value))
                conn.commit()
                bot.reply_to(message, f"<b>تم إنشاء الكود: {code}\nقيمته: {value} نقطة ✅.</b>", parse_mode='HTML')
                del user_states[user_id]
            except:
                bot.reply_to(message, "<b>أدخل رقم ❌.</b>", parse_mode='HTML')
        
        elif state == 'reset_user_id':
            try:
                target_id = int(text)
                user_states[user_id] = {'state': 'reset_amount', 'target_id': target_id}
                bot.reply_to(message, "<b>ارسل عدد النقاط التي تريد خصمها 💸:</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل ID صحيح ❌.</b>", parse_mode='HTML')
        
        elif state == 'reset_amount':
            try:
                amount = int(text)
                target_id = user_states[user_id]['target_id']
                cursor = conn.cursor()
                cursor.execute('SELECT balance FROM users WHERE user_id = ?', (target_id,))
                balance = cursor.fetchone()
                if balance:
                    balance = balance[0]
                    new_balance = balance - amount
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(
                        InlineKeyboardButton("نعم", callback_data=f"confirm_reset_{target_id}_{amount}"),
                        InlineKeyboardButton("لا", callback_data="reset_balance")
                    )
                    bot.reply_to(message, f"<b>رصيد الشخص: {balance} نقطة\nسوف يصبح: {new_balance} نقطة\nهل تؤكد ❓</b>", parse_mode='HTML', reply_markup=keyboard)
                else:
                    bot.reply_to(message, "<b>مستخدم غير موجود ❌.</b>", parse_mode='HTML')
                del user_states[user_id]
            except:
                bot.reply_to(message, "<b>أدخل رقم ❌.</b>", parse_mode='HTML')
        
        elif state == 'add_channel':
            username = text.strip()
            cursor = conn.cursor()
            try:
                admins = bot.get_chat_administrators(f'@{username}')
                bot_id = bot.get_me().id
                is_admin = any(admin.user.id == bot_id for admin in admins)
                if is_admin:
                    cursor.execute('INSERT OR IGNORE INTO mandatory_channels (channel_username) VALUES (?)', (username,))
                    cursor.execute('INSERT OR IGNORE INTO channel_stats (channel_username) VALUES (?)', (username,))
                    conn.commit()
                    bot.reply_to(message, "<b>تم إضافة القناة بنجاح ✅!</b>", parse_mode='HTML')
                else:
                    bot.reply_to(message, "<b>البوت ليس مشرفاً في القناة أو لا يملك صلاحية فحص الأعضاء ⚠️.</b>", parse_mode='HTML')
            except Exception as e:
                print(f"Error adding channel: {str(e)}")
                bot.reply_to(message, "<b>خطأ في التحقق من القناة ❌.</b>", parse_mode='HTML')
            del user_states[user_id]

        elif state == 'transfer_id':
            cursor = conn.cursor()
            try:
                target_id = int(text)
                if target_id == user_id:
                    bot.reply_to(message, "<b>لا يمكن تحويل النقاط إلى نفسك ❌.</b>", parse_mode='HTML')
                    del user_states[user_id]
                    start(message)
                    return
                cursor.execute('SELECT balance FROM users WHERE user_id = ?', (target_id,))
                if cursor.fetchone():
                    user_states[user_id]['target_id'] = target_id
                    user_states[user_id]['state'] = 'transfer_amount'
                    bot.reply_to(message, "<b>أرسل عدد النقاط التي تريد تحويلها 💸:</b>", parse_mode='HTML')
                else:
                    bot.reply_to(message, "<b>المستخدم غير موجود في البوت ❌.</b>", parse_mode='HTML')
                    del user_states[user_id]
                    start(message)
            except:
                bot.reply_to(message, "<b>أدخل ID صحيح ❌.</b>", parse_mode='HTML')
        
        elif state == 'transfer_amount':
            cursor = conn.cursor()
            try:
                amount = int(text)
                if amount <= 0:
                    bot.reply_to(message, "<b>أدخل عدد إيجابي صحيح ❌.</b>", parse_mode='HTML')
                    return
                cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
                balance = cursor.fetchone()[0]
                if amount > balance:
                    bot.reply_to(message, "<b>رصيدك غير كافي ⚠️.</b>", parse_mode='HTML')
                    del user_states[user_id]
                    start(message)
                    return
                target_id = user_states[user_id]['target_id']
                new_balance = balance - amount
                msg = f"<b>التحويل إلى ID: {target_id}\nالنقاط: {amount}\nرصيدك بعد: {new_balance}\nهل تؤكد العملية ❓</b>"
                keyboard = InlineKeyboardMarkup()
                keyboard.add(
                    InlineKeyboardButton("نعم ✅", callback_data="confirm_transfer_yes"),
                    InlineKeyboardButton("لا ❌", callback_data="confirm_transfer_no")
                )
                bot.reply_to(message, msg, parse_mode='HTML', reply_markup=keyboard)
                user_states[user_id]['amount'] = amount
            except:
                bot.reply_to(message, "<b>أدخل رقم صحيح ❌.</b>", parse_mode='HTML')
        
        elif state == 'transfer_captcha':
            cursor = conn.cursor()
            if int(text) == user_states[user_id]['captcha_code']:
                amount = user_states[user_id]['amount']
                target_id = user_states[user_id]['target_id']
                cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
                cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, target_id))
                conn.commit()
                bot.reply_to(message, f"<b>تم تحويل {amount} نقطة بنجاح ✅!\nشكراً لاستخدامك فولو ميديا 🥰</b>", parse_mode='HTML')
                try:
                    bot.send_message(target_id, f"<b>لقد تلقيت {amount} نقطة من ID: {user_id} 🎁!</b>", parse_mode='HTML')
                except:
                    pass
                del user_states[user_id]
                start(message)
            else:
                bot.reply_to(message, "<b>رمز خاطئ، تم إلغاء التحويل ❌.</b>", parse_mode='HTML')
                del user_states[user_id]
                start(message)
        
        elif state == 'funding_quantity':
            cursor = conn.cursor()
            try:
                quantity = int(text)
                min_members = 40
                max_members = user_states[user_id]['max_members']
                if quantity < min_members or quantity > max_members:
                    bot.reply_to(message, f"<b>العدد يجب أن يكون بين {min_members} و {max_members} ⚠️.</b>", parse_mode='HTML')
                    return
                user_states[user_id]['quantity'] = quantity
                user_states[user_id]['state'] = 'funding_channel'
                bot.reply_to(message, "<b>أرسل معرف القناة أو المجموعة (مثل @SYR_SB):</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل رقم صحيح ❌.</b>", parse_mode='HTML')
        
        elif state == 'funding_channel':
            cursor = conn.cursor()
            channel_username = text.strip().lstrip('@')
            try:
                admins = bot.get_chat_administrators(f'@{channel_username}')
                bot_id = bot.get_me().id
                is_admin = any(admin.user.id == bot_id and admin.can_invite_users for admin in admins)
                if is_admin:
                    quantity = user_states[user_id]['quantity']
                    cost = quantity * 8
                    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
                    balance = cursor.fetchone()[0]
                    msg = f"<b>تم التحقق من القناة بنجاح ✅\nالقناة: @{channel_username}\nالعدد المطلوب: {quantity} عضو\nالتكلفة: {cost} نقطة\nرصيدك: {balance}\nهل ترغب في إتمام العملية؟</b>"
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(
                        InlineKeyboardButton("نعم ✅", callback_data="confirm_funding_yes"),
                        InlineKeyboardButton("لا ❌", callback_data="confirm_funding_no")
                    )
                    bot.reply_to(message, msg, parse_mode='HTML', reply_markup=keyboard)
                    user_states[user_id]['channel_username'] = channel_username
                else:
                    bot.reply_to(message, "<b>البوت ليس مشرفًا أو لا يملك صلاحية دعوة المستخدمين ⚠️.</b>", parse_mode='HTML')
            except Exception as e:
                print(f"Error in funding_channel: {str(e)}")
                bot.reply_to(message, "<b>خطأ في التحقق من القناة. تأكد من أنها عامة وموجودة ❌.</b>", parse_mode='HTML')
            # لا تحذف user_states هنا، لأنها مطلوبة للتأكيد

# دالة للحصول على فئة الخدمة
def get_category(service_name):
    cursor = conn.cursor()
    cursor.execute('SELECT category FROM services WHERE name = ?', (service_name,))
    result = cursor.fetchone()
    return result[0] if result else "🌐 خدمات عامة"

# نسخ احتياطي تلقائي كل 24 ساعة
def send_backup():
    bot.send_document(DEVELOPER_ID, open('bot_database.db', 'rb'), caption="<b>نسخ احتياطي للبيانات 📂. سأرسل كل 24 ساعة.</b>", parse_mode='HTML')

def backup_thread():
    while True:
        send_backup()
        time.sleep(86400)  # 24 ساعة

# بدء النسخ الاحتياطي في خيط منفصل
threading.Thread(target=backup_thread).start()

# تشغيل البوت
bot.infinity_polling(timeout=10, long_polling_timeout=5)        