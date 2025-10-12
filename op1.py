import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import random
import string
import time
import threading
import os

#توكن البوت
BOT_TOKEN = '7524766252:AAFfFAFCMrtloJeCFI_4auUD_ahvuyaONzQ'
DEVELOPER_ID = 6789179634  # ايدي المطور
GROUP_ID = -1002633150607  # ID المجموعة لإرسال الطلبات

bot = telebot.TeleBot(BOT_TOKEN)


conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()


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
    status TEXT DEFAULT 'pending'
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    name TEXT,
    price_per_1000 INTEGER,
    min_quantity INTEGER,
    max_quantity INTEGER
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

conn.commit()


user_states = {}  


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


def show_mandatory_channels(message):
    cursor.execute('SELECT channel_username FROM mandatory_channels')
    channels = cursor.fetchall()
    if not channels:
        bot.send_message(message.chat.id, "لا توجد قنوات إجبارية حالياً.")
        return
    keyboard = InlineKeyboardMarkup()
    for channel in channels:
        keyboard.add(InlineKeyboardButton(f"اشترك في @{channel[0]}", url=f"https://t.me/{channel[0]}"))
    keyboard.add(InlineKeyboardButton("إعادة المحاولة", callback_data="retry_subscription"))
    bot.send_message(message.chat.id, "<b>أنت غير مشترك في قنوات البوت. اشترك واضغط إعادة المحاولة:</b>", parse_mode='HTML', reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id == DEVELOPER_ID:
        show_developer_panel(message)
        return
    
    
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)', (user_id,))
    conn.commit()
    
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    balance = cursor.fetchone()[0]
    
    if not check_subscription(user_id):
        show_mandatory_channels(message)
        return
    
    update_channel_stats(user_id)  
    
    welcome = f"<b>اهلا بك عزيزي في بوت خدماتكم👋</b>\n\n💰›رصـيـدك : {balance}\n⬅️›ايـديـك: {user_id}"
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


def show_developer_panel(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("اضف خدمة جديدة", callback_data="add_service"),
        InlineKeyboardButton("حذف خدمة", callback_data="delete_service"),
        InlineKeyboardButton("انشاء كود فريد", callback_data="create_code"),
        InlineKeyboardButton("تصفير رصيد", callback_data="reset_balance"),
        InlineKeyboardButton("اضافة قنوات اجباري", callback_data="add_mandatory_channel"),
        InlineKeyboardButton("قنوات الاجباري", callback_data="mandatory_channels"),
        InlineKeyboardButton("معلومات القنوات", callback_data="channels_info"),
        InlineKeyboardButton("جلب ملفات تخزين", callback_data="backup_files")
    )
    bot.send_message(message.chat.id, "<b>اهلا بك عزيزي المطور ⚙️👋</b>", parse_mode='HTML', reply_markup=keyboard)


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
        service_name = data.split("_", 1)[1]  
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
        bot.answer_callback_query(call.id, f"رصيدك الحالي: {balance} 💰", show_alert=True)
    
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
    
    #المطور ولوحته
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
        category = data.split("_")[2]
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
        category = data.split("_")[2]
        cursor.execute('SELECT name FROM services WHERE category = ?', (category,))
        services = cursor.fetchall()
        keyboard = InlineKeyboardMarkup(row_width=2)
        for service in services:
            keyboard.add(InlineKeyboardButton(service[0], callback_data=f"del_service_{service[0]}"))
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="delete_service"))
        bot.edit_message_text(f"<b>خدمات {category} لحذفها:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("del_service_"):
        service_name = data.split("del_service_")[1]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("نعم", callback_data=f"confirm_del_service_{service_name}"),
            InlineKeyboardButton("لا", callback_data="delete_service")
        )
        bot.edit_message_text(f"<b>هل ترغب بحذف الخدمة '{service_name}' نهائياً ❓</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("confirm_del_service_"):
        service_name = data.split("confirm_del_service_")[1]
        cursor.execute('DELETE FROM services WHERE name = ?', (service_name,))
        conn.commit()
        bot.edit_message_text("<b>تم حذف الخدمة بنجاح ✅.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "create_code":
        user_states[user_id] = {'state': 'create_code_value'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل الكمية التي تريد إضافتها (مثل: 10) 💵:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "reset_balance":
        user_states[user_id] = {'state': 'reset_user_id'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل ID الشخص 🔢:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "add_mandatory_channel":
        user_states[user_id] = {'state': 'add_channel'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text("<b>ارسل يوزر القناة (بدون @) 📢:</b>", call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "mandatory_channels":
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
        cursor.execute('DELETE FROM mandatory_channels WHERE channel_username = ?', (channel,))
        cursor.execute('DELETE FROM channel_stats WHERE channel_username = ?', (channel,))
        cursor.execute('DELETE FROM user_subscriptions WHERE channel_username = ?', (channel,))
        conn.commit()
        bot.edit_message_text("<b>تم الحذف بنجاح ✅.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "channels_info":
        cursor.execute('SELECT channel_username, subscribers_count FROM channel_stats')
        stats = cursor.fetchall()
        msg = "<b>معلومات القنوات 📈:</b>\n"
        for stat in stats:
            msg += f"@{stat[0]} - مشتركين عبر البوت: {stat[1]}\n"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("رجوع", callback_data="dev_back"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "backup_files":
        send_backup()
        bot.answer_callback_query(call.id, "تم إرسال الملفات 📂.", show_alert=True)
    
    elif data == "dev_back":
        bot.delete_message(call.message.chat.id, call.message.id)
        show_developer_panel(call.message)
    
    elif data == "retry_subscription":
        if check_subscription(user_id):
            bot.delete_message(call.message.chat.id, call.message.id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "ما زلت غير مشترك. اشترك أولاً! ⚠️", show_alert=True)
    
    
    elif data.startswith("confirm_order_"):
        order_id = data.split("confirm_order_")[1]
        cursor.execute('UPDATE orders SET status = "تم التنفيذ" WHERE order_id = ?', (order_id,))
        conn.commit()
        bot.edit_message_text(call.message.text + "\n\n<b>تم التنفيذ ✅</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
        bot.answer_callback_query(call.id, "تم تغيير الحالة إلى تم التنفيذ.", show_alert=True)
    
    elif data.startswith("cancel_order_"):
        order_id = data.split("cancel_order_")[1]
        bot.edit_message_text(call.message.text + "\n\n<b>تم الإلغاء ❌</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
        bot.answer_callback_query(call.id, "تم إلغاء الطلب.", show_alert=True)
    
    
    elif data.startswith("confirm_reset_"):
        parts = data.split("_")
        target_id = int(parts[2])
        amount = int(parts[3])
        cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (amount, target_id))
        conn.commit()
        bot.edit_message_text("<b>تم الخصم بنجاح ✅.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
    
    elif data == "confirm_link_yes":
        if user_id in user_states and 'link' in user_states[user_id]:
            link = user_states[user_id]['link']
            service = user_states[user_id]['service']
            quantity = user_states[user_id]['quantity']
            cursor.execute('SELECT price_per_1000 FROM services WHERE name = ?', (service,))
            price_per_1000 = cursor.fetchone()[0]
            total_price = (quantity / 1000) * price_per_1000
            
            cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            balance = cursor.fetchone()[0]
            if balance < total_price:
                bot.edit_message_text("<b>رصيدك غير كافي ⚠️.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
                del user_states[user_id]
                return
            
            
            new_balance = balance - total_price
            cursor.execute('UPDATE users SET balance = ?, total_orders = total_orders + 1 WHERE user_id = ?', (new_balance, user_id))
            
            
            cursor.execute('INSERT INTO orders (user_id, service_name, quantity, link, price) VALUES (?, ?, ?, ?, ?)', (user_id, service, quantity, link, total_price))
            order_id = cursor.lastrowid
            conn.commit()
            
            
            user_info = bot.get_chat(user_id)
            username = user_info.username if user_info.username else "لا يوجد"
            group_msg = f"<b>طلب جديد 💼:</b>\nID: {order_id}\nمستخدم: {user_id} (@{username})\nخدمة: {service}\nكمية: {quantity}\nرابط: {link}\nسعر: {total_price}"
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton("نعم", callback_data=f"confirm_order_{order_id}"),
                InlineKeyboardButton("لا", callback_data=f"cancel_order_{order_id}")
            )
            bot.send_message(GROUP_ID, group_msg, parse_mode='HTML', reply_markup=keyboard)
            
            msg = f"<b>تم تنفيذ طلبك بنجاح ✅!</b>\nID الطلب: {order_id}\nالسعر: {total_price}\nتبقى من رصيدك: {new_balance}\n\nاضغط /start للبداية من جديد."
            bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML')
            del user_states[user_id]
        else:
            bot.answer_callback_query(call.id, "خطأ في التأكيد.", show_alert=True)
    
    elif data == "confirm_link_no":
        bot.edit_message_text("<b>حسنا، تم الإلغاء ❌. ارسل /start من جديد.</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
        if user_id in user_states:
            del user_states[user_id]


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
        
        elif state == 'use_code':
            code = text.upper()
            cursor.execute('SELECT value, used FROM codes WHERE code = ?', (code,))
            code_info = cursor.fetchone()
            if code_info and code_info[1] == 0:
                value = code_info[0]
                cursor.execute('UPDATE users SET balance = balance + ?, total_charged = total_charged + ? WHERE user_id = ?', (value, value, user_id))
                cursor.execute('UPDATE codes SET used = 1 WHERE code = ?', (code,))
                conn.commit()
                bot.reply_to(message, f"<b>تم إضافة {value} إلى رصيدك بنجاح ✅!</b>", parse_mode='HTML')
            else:
                bot.reply_to(message, "<b>هذا الكود غير صالح أو مستخدم ❌.</b>", parse_mode='HTML')
            del user_states[user_id]
        
        elif state == 'order_info':
            try:
                order_id = int(text)
                cursor.execute('SELECT service_name, quantity, link, price, status FROM orders WHERE order_id = ? AND user_id = ?', (order_id, user_id))
                order = cursor.fetchone()
                if order:
                    msg = f"<b>معلومات الطلب {order_id} 🔍:</b>\nخدمة: {order[0]}\nكمية: {order[1]}\nرابط: {order[2]}\nسعر: {order[3]}\nحالة: {order[4]}"
                    bot.reply_to(message, msg, parse_mode='HTML')
                else:
                    bot.reply_to(message, "<b>طلب غير موجود ❌.</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل ID صحيح ❌.</b>", parse_mode='HTML')
            del user_states[user_id]
        
        # حالات المطور
        elif state == 'add_service_name' and user_id == DEVELOPER_ID:
            name = text
            user_states[user_id] = {'state': 'add_price', 'category': user_states[user_id]['category'], 'name': name}
            bot.reply_to(message, "<b>ارسل السعر لكل 1000 (مثل: 100) 💲:</b>", parse_mode='HTML')
        
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
                category = user_states[user_id]['category']
                name = user_states[user_id]['name']
                price = user_states[user_id]['price']
                min_q = user_states[user_id]['min']
                cursor.execute('INSERT INTO services (category, name, price_per_1000, min_quantity, max_quantity) VALUES (?, ?, ?, ?, ?)', (category, name, price, min_q, max_q))
                conn.commit()
                bot.reply_to(message, "<b>تم إضافة الخدمة بنجاح ✅!</b>", parse_mode='HTML')
                del user_states[user_id]
            except:
                bot.reply_to(message, "<b>أدخل رقم ❌.</b>", parse_mode='HTML')
        
        elif state == 'create_code_value':
            try:
                value = int(text)
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(4,6)))
                cursor.execute('INSERT INTO codes (code, value) VALUES (?, ?)', (code, value))
                conn.commit()
                bot.reply_to(message, f"<b>تم إنشاء الكود: {code}\nقيمته: {value} دولار ✅.</b>", parse_mode='HTML')
                del user_states[user_id]
            except:
                bot.reply_to(message, "<b>أدخل رقم ❌.</b>", parse_mode='HTML')
        
        elif state == 'reset_user_id':
            try:
                target_id = int(text)
                user_states[user_id] = {'state': 'reset_amount', 'target_id': target_id}
                bot.reply_to(message, "<b>ارسل العدد الذي تريد خصمه 💸:</b>", parse_mode='HTML')
            except:
                bot.reply_to(message, "<b>أدخل ID صحيح ❌.</b>", parse_mode='HTML')
        
        elif state == 'reset_amount':
            try:
                amount = int(text)
                target_id = user_states[user_id]['target_id']
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
                    bot.reply_to(message, f"<b>رصيد الشخص: {balance}\nسوف يصبح: {new_balance}\nهل تؤكد ❓</b>", parse_mode='HTML', reply_markup=keyboard)
                else:
                    bot.reply_to(message, "<b>مستخدم غير موجود ❌.</b>", parse_mode='HTML')
                del user_states[user_id]
            except:
                bot.reply_to(message, "<b>أدخل رقم ❌.</b>", parse_mode='HTML')
        
        elif state == 'add_channel':
            username = text.strip()
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
            except:
                bot.reply_to(message, "<b>خطأ في التحقق من القناة ❌.</b>", parse_mode='HTML')
            del user_states[user_id]


def get_category(service_name):
    cursor.execute('SELECT category FROM services WHERE name = ?', (service_name,))
    return cursor.fetchone()[0]

# نسخ احتياطي 
def send_backup():
    bot.send_document(DEVELOPER_ID, open('bot_database.db', 'rb'), caption="<b>نسخ احتياطي للبيانات 📂. سأرسل كل 24 ساعة.</b>", parse_mode='HTML')

def backup_thread():
    while True:
        send_backup()
        time.sleep(86400)  

# خيط النسخ الأحتياطي 
threading.Thread(target=backup_thread).start()

# تشغيل البوت
bot.infinity_polling()