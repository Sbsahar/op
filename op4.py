import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import sqlite3
import random
import string
import time
import threading
import os
import api_handler  # استيراد الملف الجديد للتعامل مع الـ API

# استبدل هذه المتغيرات
BOT_TOKEN = '7524766252:AAFfFAFCMrtloJeCFI_4auUD_ahvuyaONzQ'
DEVELOPER_ID = 6789179634  # ايدي المطور
GROUP_ID = -1002091669531  # ID المجموعة لإرسال الطلبات

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

# إنشاء قاعدة البيانات
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()

# إنشاء الجداول إذا لم تكن موجودة
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    total_charged INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service_name TEXT,
    quantity INTEGER,
    link TEXT,
    price INTEGER,
    status TEXT DEFAULT 'pending',
    api_order_id INTEGER DEFAULT NULL
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
    subscribers_count INTEGER DEFAULT 0
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS user_subscriptions (
    user_id INTEGER,
    channel_username TEXT,
    PRIMARY KEY (user_id, channel_username)
)''')

# تحديث جدول services لإضافة عمود api_service_id إذا لم يكن موجودًا
try:
    cursor.execute('ALTER TABLE services ADD COLUMN api_service_id INTEGER')
except sqlite3.OperationalError:
    pass

# تحديث جدول services لإضافة عمود note إذا لم يكن موجودًا
try:
    cursor.execute('ALTER TABLE services ADD COLUMN note TEXT DEFAULT ""')
except sqlite3.OperationalError:
    pass

# تحديث جدول orders لإضافة عمود api_order_id إذا لم يكن موجودًا
try:
    cursor.execute('ALTER TABLE orders ADD COLUMN api_order_id INTEGER DEFAULT NULL')
except sqlite3.OperationalError:
    pass

# تحديث جدول users لإضافة عمود username إذا لم يكن موجودًا
try:
    cursor.execute('ALTER TABLE users ADD COLUMN username TEXT DEFAULT ""')
except sqlite3.OperationalError:
    pass

conn.commit()

# متغيرات مؤقتة للتفاعلات
user_states = {}  # لحفظ حالة المستخدم (مثل إضافة خدمة، إلخ)

# فحص الاشتراك في القنوات
def check_subscription(user_id):
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

# تحديث إحصائيات القنوات فقط للمستخدمين الجدد
def update_channel_stats(user_id):
    cursor.execute('SELECT channel_username FROM mandatory_channels')
    channels = cursor.fetchall()
    updated = False
    for channel in channels:
        ch_username = channel[0]
        cursor.execute('SELECT * FROM user_subscriptions WHERE user_id = ? AND channel_username = ?', (user_id, ch_username))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO user_subscriptions (user_id, channel_username) VALUES (?, ?)', (user_id, ch_username))
            cursor.execute('UPDATE channel_stats SET subscribers_count = subscribers_count + 1 WHERE channel_username = ?', (ch_username,))
            updated = True
    if updated:
        conn.commit()

# عرض قنوات الإجباري للمستخدم
def show_mandatory_channels(message):
    cursor.execute('SELECT channel_username FROM mandatory_channels')
    channels = cursor.fetchall()
    if not channels:
        bot.send_message(message.chat.id, "لا توجد قنوات إجبارية حالياً.")
        return
    keyboard = InlineKeyboardMarkup()
    for channel in channels:
        keyboard.add(InlineKeyboardButton(f"اشترك في @{channel[0]}", url=f"https://t.me/{channel[0]}"))
    bot.send_message(message.chat.id, "<b>أنت غير مشترك في قنوات البوت. اشترك وأعد المحاولة /start</b>", parse_mode='HTML', reply_markup=keyboard)

# ستارت المستخدمين
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id == DEVELOPER_ID:
        show_developer_panel(message)
        return
    
    # إضافة المستخدم إذا جديد
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)', (user_id,))
    conn.commit()
    
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    balance = cursor.fetchone()[0]
    
    if not check_subscription(user_id):
        show_mandatory_channels(message)
        return
    
    update_channel_stats(user_id)  # تحديث الإحصائيات فقط إذا جديد
    
    welcome = f"<b>اهلا بك عزيزي في بوت فولو ميديا👋</b>\n\n💰›رصـيـدك : {balance} نقطة\n⬅️›ايـديـك: {user_id}"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("الخدمات", callback_data="services"),
        InlineKeyboardButton("الرصيد", callback_data="balance"),
        InlineKeyboardButton("طلباتي", callback_data="my_orders"),
        InlineKeyboardButton("اضف رصيد", callback_data="add_balance"),
        InlineKeyboardButton("استخدام كود", callback_data="use_code"),
        InlineKeyboardButton("احصائيات البوت", callback_data="bot_stats"),
        InlineKeyboardButton("معلومات الطلب", callback_data="order_info"),
        InlineKeyboardButton("الحساب", callback_data="account")
    )
    bot.send_message(message.chat.id, welcome, parse_mode='HTML', reply_markup=keyboard)

# لوحة المطور
def show_developer_panel(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("اضف خدمة جديدة", callback_data="add_service"),
        InlineKeyboardButton("حذف خدمة", callback_data="delete_service"),
        InlineKeyboardButton("انشاء كود فريد", callback_data="create_code"),
        InlineKeyboardButton("تصفير رصيد", callback_data="reset_balance"),
        InlineKeyboardButton("فحص طلبات", callback_data="check_orders"),
        InlineKeyboardButton("اضافة قنوات اجباري", callback_data="add_mandatory_channel"),
        InlineKeyboardButton("قنوات الاجباري", callback_data="mandatory_channels"),
        InlineKeyboardButton("معلومات القنوات", callback_data="channels_info"),
        InlineKeyboardButton("جلب ملفات تخزين", callback_data="backup_files")
    )
    bot.send_message(message.chat.id, "<b>اهلا بك عزيزي المطور ⚙️👋</b>", parse_mode='HTML', reply_markup=keyboard)

# معالجة الضغط على الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if data == "services":
        keyboard = InlineKeyboardMarkup(row_width=2)
        categories = ["خدمات مجانية", "خدمات تلغرام", "خدمات انستغرام", "خدمات فيسبوك", "خدمات تويتر", "خدمات تيك توك", "خدمات يوتيوب", "خدمات تويتش", "خدمات ديسكورد", "خدمات سناب شات", "خدمات عامة"]
        for cat in categories:
            keyboard.add(InlineKeyboardButton(cat, callback_data=f"category_{cat}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_start"))
        bot.edit_message_text("<b>اختر فئة الخدمات:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("category_"):
        category = data.split("_")[1]
        cursor.execute('SELECT name FROM services WHERE category = ?', (category,))
        services = cursor.fetchall()
        keyboard = InlineKeyboardMarkup(row_width=2)
        for service in services:
            keyboard.add(InlineKeyboardButton(service[0], callback_data=f"service_{service[0]}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="services"))
        bot.edit_message_text(f"<b>خدمات {category}:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("service_"):
        service_name = data.split("_")[1]
        cursor.execute('SELECT price_per_1000, min_quantity, max_quantity FROM services WHERE name = ?', (service_name,))
        details = cursor.fetchone()
        if details:
            price, min_q, max_q = details
            msg = f"<b>{service_name}</b>\n\n] السعر : {price} نقطة لكل 1000\n] اقل طلب : {min_q}\n] اكبر طلب : {max_q}\n\nارسل الكمية التي تريدها:"
            user_states[user_id] = {'state': 'quantity', 'service': service_name, 'price': price, 'min': min_q, 'max': max_q}
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("رجوع", callback_data=f"category_{get_category(service_name)}"))
            bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)

    elif data == "balance":
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        balance = cursor.fetchone()[0]
        bot.answer_callback_query(call.id, f"رصيدك الحالي: {balance} نقطة 💰", show_alert=True)
    
    elif data == "my_orders":
        cursor.execute('SELECT order_id, service_name, status FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 5', (user_id,))
        orders = cursor.fetchall()
        msg = "<b>آخر 5 طلبات 💼:</b>\n"
        for order in orders:
            msg += f"ID: {order[0]} - {order[1]} - حالة: {order[2]}\n"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_start"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "add_balance":
        bot.edit_message_text("<b>لإضافة رصيد، تواصل مع المطور 📞.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
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
        msg = f"<b>احصائيات البوت 📊:</b>\nعدد المستخدمين: {users_count}\nعدد الطلبات: {orders_count}"
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
        msg = f"<b>معلومات حسابك 👤:</b>\nرصيد حالي: {info[0]}\nإجمالي الشحن: {info[1]}\nإجمالي الطلبات: {info[2]}"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="back_to_start"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "back_to_start":
        bot.delete_message(call.message.chat.id, call.message.id)
        start(call.message)
    
    # لوحة المطور
    if user_id != DEVELOPER_ID:
        return
    
    if data == "add_service":
        keyboard = InlineKeyboardMarkup(row_width=2)
        categories = ["خدمات مجانية", "خدمات تلغرام", "خدمات انستغرام", "خدمات فيسبوك", "خدمات تويتر", "خدمات تيك توك", "خدمات يوتيوب", "خدمات تويتش", "خدمات ديسكورد", "خدمات سناب شات", "خدمات عامة"]
        for cat in categories:
            keyboard.add(InlineKeyboardButton(cat, callback_data=f"add_cat_{cat}"))
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
        categories = ["خدمات مجانية", "خدمات تلغرام", "خدمات انستغرام", "خدمات فيسبوك", "خدمات تويتر", "خدمات تيك توك", "خدمات يوتيوب", "خدمات تويتش", "خدمات ديسكورد", "خدمات سناب شات", "خدمات عامة"]
        for cat in categories:
            keyboard.add(InlineKeyboardButton(cat, callback_data=f"del_cat_{cat}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>اختر فئة الخدمة لحذفها 🗑️:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("del_cat_"):
        category = data.split("del_cat_")[1]
        cursor.execute('SELECT name FROM services WHERE category = ?', (category,))
        services = cursor.fetchall()
        keyboard = InlineKeyboardMarkup(row_width=2)
        for service in services:
            keyboard.add(InlineKeyboardButton(service[0], callback_data=f"del_service_{service[0]}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="delete_service"))
        bot.edit_message_text(f"<b>خدمات {category} لحذفها:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("del_service_"):
        service_name = data.split("del_service_")[1]
        cursor.execute('DELETE FROM services WHERE name = ?', (service_name,))
        conn.commit()
        bot.edit_message_text("<b>تم حذف الخدمة بنجاح ✅.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "create_code":
        user_states[user_id] = {'state': 'create_code_value'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل عدد النقاط التي تريد إضافتها (مثل: 10):</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "reset_balance":
        user_states[user_id] = {'state': 'reset_user_id'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل ID الشخص:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "add_mandatory_channel":
        user_states[user_id] = {'state': 'add_channel'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل يوزر القناة (بدون @):</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "mandatory_channels":
        cursor.execute('SELECT channel_username FROM mandatory_channels')
        channels = cursor.fetchall()
        keyboard = InlineKeyboardMarkup()
        for channel in channels:
            keyboard.add(InlineKeyboardButton(f"@{channel[0]}", callback_data=f"del_channel_{channel[0]}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>قنوات الإجباري:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("del_channel_"):
        channel = data.split("del_channel_")[1]
        cursor.execute('DELETE FROM mandatory_channels WHERE channel_username = ?', (channel,))
        conn.commit()
        bot.edit_message_text("<b>تم الحذف بنجاح.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "channels_info":
        cursor.execute('SELECT channel_username, subscribers_count FROM channel_stats')
        stats = cursor.fetchall()
        msg = "<b>معلومات القنوات:</b>\n"
        for stat in stats:
            msg += f"@{stat[0]} - مشتركين: {stat[1]}\n"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "backup_files":
        bot.send_document(call.message.chat.id, open('bot_database.db', 'rb'))
        bot.answer_callback_query(call.id, "تم إرسال الملف.")
    
    elif data == "dev_back":
        bot.delete_message(call.message.chat.id, call.message.id)
        show_developer_panel(call.message)
    
# دالة للحصول على فئة الخدمة
def get_category(service_name):
    cursor.execute('SELECT category FROM services WHERE name = ?', (service_name,))
    return cursor.fetchone()[0]

# نسخ احتياطي تلقائي كل 24 ساعة
def send_backup():
    bot.send_document(DEVELOPER_ID, open('bot_database.db', 'rb'), caption="<b>نسخ احتياطي للبيانات.</b>", parse_mode='HTML')

def backup_thread():
    while True:
        send_backup()
        time.sleep(86400)  # 24 ساعة

# بدء النسخ الاحتياطي في خيط منفصل
threading.Thread(target=backup_thread).start()

# تشغيل البوت
while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Error occurred: {str(e)}. Restarting bot...")
        time.sleep(5)
        continue
