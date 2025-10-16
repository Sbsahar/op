import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import sqlite3
import random
import string
import time
import threading
import os
import api_handler  # ملف الـ API الجديد

# إعدادات البوت
BOT_TOKEN = '7524766252:AAFfFAFCMrtloJeCFI_4auUD_ahvuyaONzQ'
DEVELOPER_ID = 6789179634
GROUP_ID = -1002091669531  # ID المجموعة لإرسال تفاصيل الطلبات

bot = telebot.TeleBot(BOT_TOKEN)

# إعداد أوامر البوت
def set_bot_commands():
    commands = [
        BotCommand("start", "ابدأ من جديد"),
        BotCommand("help", "تعليمات وقوانين البوت"),
        BotCommand("status", "حالة آخر طلب")
    ]
    bot.set_my_commands(commands)

set_bot_commands()

# إعداد قاعدة البيانات
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()

# إنشاء الجداول
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    total_charged INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    username TEXT DEFAULT ''
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service_name TEXT,
    api_service_id INTEGER,
    quantity INTEGER,
    link TEXT,
    price INTEGER,
    status TEXT DEFAULT 'pending',
    api_order_id TEXT DEFAULT NULL,
    api_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    name TEXT,
    api_service_id INTEGER,
    price_per_1000 INTEGER,
    min_quantity INTEGER,
    max_quantity INTEGER,
    note TEXT DEFAULT '',
    api_rate REAL DEFAULT 0,
    refill BOOLEAN DEFAULT 0,
    cancel BOOLEAN DEFAULT 0
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    value INTEGER,
    used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# متغيرات التفاعل
user_states = {}

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
        bot.send_message(message.chat.id, "<b>لا توجد قنوات إجبارية حالياً.</b>", parse_mode='HTML')
        start(message)
        return
    keyboard = InlineKeyboardMarkup()
    for channel in channels:
        keyboard.add(InlineKeyboardButton(f"اشترك في @{channel[0]}", url=f"https://t.me/{channel[0]}"))
    keyboard.add(InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="retry_subscription"))
    bot.send_message(message.chat.id, "<b>أنت غير مشترك في قنوات البوت. اشترك بالقنوات التالية 👇🏻 واضغط تحقق:</b>", parse_mode='HTML', reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "غير محدد"
    
    if user_id == DEVELOPER_ID:
        show_developer_panel(message)
        return
    
    # إضافة/تحديث المستخدم
    cursor.execute('INSERT OR REPLACE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    balance = cursor.fetchone()[0]
    
    if not check_subscription(user_id):
        show_mandatory_channels(message)
        return
    
    update_channel_stats(user_id)
    
    welcome = f"<b>👋 أهلا بك في بوت KD Media SMM</b>\n\n💰 رصيدك: {balance:,} نقطة\n🆔 أيديك: <code>{user_id}</code>\n👤 المستخدم: @{username}"
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💼 الخدمات", callback_data="services"),
        InlineKeyboardButton("💎 الرصيد", callback_data="balance")
    )
    keyboard.add(
        InlineKeyboardButton("📋 طلباتي", callback_data="my_orders"),
        InlineKeyboardButton("➕ شحن رصيد", callback_data="add_balance")
    )
    keyboard.add(
        InlineKeyboardButton("🎟️ كود خصم", callback_data="use_code"),
        InlineKeyboardButton("📊 إحصائيات", callback_data="bot_stats")
    )
    keyboard.add(InlineKeyboardButton("📄 المساعدة", callback_data="help"))
    
    bot.send_message(message.chat.id, welcome, parse_mode='HTML', reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
<b>📚 دليل استخدام بوت KD Media SMM</b>

<b>🔹 كيفية الطلب:</b>
1️⃣ اختر الخدمة المطلوبة
2️⃣ أدخل الكمية المطلوبة
3️⃣ أرسل الرابط (يجب أن يكون عام)
4️⃣ سيتم خصم الرصيد وإرسال الطلب للـ API

<b>⚠️ شروط الروابط:</b>
• حسابات إنستغرام: يجب أن تكون عامة
• قنوات تليجرام: يجب أن تكون عامة أو لها رابط دعوة
• يوتيوب: رابط القناة أو الفيديو

<b>💰 حساب السعر:</b>
السعر = (الكمية ÷ 1000) × سعر الـ 1000

<b>📊 حالات الطلب:</b>
• Pending: في الانتظار
• In progress: قيد التنفيذ  
• Partial: جزئي التنفيذ
• Completed: مكتمل
• Cancelled: ملغى

<b>🆘 في حالة المشاكل:</b>
• رصيد غير كافي
• رابط غير صحيح
• خدمة غير متاحة
• مشاكل في الـ API

<b>📞 الدعم الفني:</b> تواصل مع المطور
    """
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['status'])
def check_last_order(message):
    user_id = message.from_user.id
    cursor.execute('''SELECT order_id, service_name, status, api_order_id, created_at 
                      FROM orders WHERE user_id = ? 
                      ORDER BY order_id DESC LIMIT 1''', (user_id,))
    order = cursor.fetchone()
    
    if order:
        status_msg = f"""
<b>📦 آخر طلب لك #{order[0]}</b>

🛠️ الخدمة: {order[1]}
📊 الحالة: <b>{order[2]}</b>
🆔 API ID: <code>{order[3] or 'غير متوفر'}</code>
⏰ التاريخ: {order[4]}

لمعلومات مفصلة استخدم /track [ID]
        """
        bot.send_message(message.chat.id, status_msg, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "❌ لم تجد طلبات سابقة", parse_mode='HTML')

# تحديث الخدمات من API
def update_services_from_api():
    try:
        services_response = api_handler.get_services()
        if 'error' in services_response:
            print(f"❌ خطأ في جلب الخدمات: {services_response}")
            return False
        
        # مسح الخدمات القديمة
        cursor.execute('DELETE FROM services')
        
        added_count = 0
        for service in services_response:
            try:
                cursor.execute('''
                    INSERT INTO services 
                    (category, name, api_service_id, price_per_1000, min_quantity, max_quantity, 
                     api_rate, refill, cancel, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    service.get('category', 'عامة'),
                    service.get('name', f'خدمة {service.get("service")}'),
                    int(service.get('service', 0)),
                    int(float(service.get('rate', 0)) * 1000),  # السعر لكل 1000
                    int(service.get('min', 0)),
                    int(service.get('max', 10000)),
                    float(service.get('rate', 0)),
                    1 if service.get('refill') else 0,
                    1 if service.get('cancel') else 0,
                    ''
                ))
                added_count += 1
            except Exception as e:
                print(f"خطأ في إضافة خدمة {service.get('service')}: {e}")
        
        conn.commit()
        print(f"✅ تم تحديث {added_count} خدمة من KD Media API")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحديث الخدمات: {str(e)}")
        return False

# لوحة المطور
def show_developer_panel(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔄 تحديث الخدمات", callback_data="update_services_api"),
        InlineKeyboardButton("💰 فحص الرصيد API", callback_data="check_api_balance")
    )
    keyboard.add(
        InlineKeyboardButton("➕ إضافة خدمة", callback_data="add_service"),
        InlineKeyboardButton("🗑️ حذف خدمة", callback_data="delete_service")
    )
    keyboard.add(
        InlineKeyboardButton("🎟️ إنشاء كود", callback_data="create_code"),
        InlineKeyboardButton("📊 إحصائيات", callback_data="dev_stats")
    )
    keyboard.add(
        InlineKeyboardButton("🔍 فحص طلب", callback_data="check_order"),
        InlineKeyboardButton("📤 نسخ احتياطي", callback_data="backup_files")
    )
    keyboard.add(InlineKeyboardButton("🔙 العودة", callback_data="back_to_start"))
    
    bot.send_message(message.chat.id, "<b>⚙️ لوحة تحكم المطور - KD Media SMM</b>", parse_mode='HTML', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if user_id != DEVELOPER_ID and data.startswith(('add_', 'del_', 'dev_', 'update_', 'check_')):
        bot.answer_callback_query(call.id, "🚫 هذا القسم للمطور فقط", show_alert=True)
        return
    
    if data == "services":
        # فئات الخدمات من قاعدة البيانات
        cursor.execute('SELECT DISTINCT category FROM services ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        for category in categories:
            keyboard.add(InlineKeyboardButton(f"📂 {category}", callback_data=f"category_{category}"))
        keyboard.add(InlineKeyboardButton("🔄 تحديث الخدمات", callback_data="update_services_api"))
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="back_to_start"))
        
        bot.edit_message_text("<b>🎯 اختر فئة الخدمات:</b>", call.message.chat.id, call.message.id, 
                            parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("category_"):
        category = data.split("category_")[1]
        cursor.execute('SELECT id, name, price_per_1000 FROM services WHERE category = ? ORDER BY name', (category,))
        services = cursor.fetchall()
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        for service in services:
            service_text = f"{service[1]} - {service[2]}ن/1000"
            keyboard.add(InlineKeyboardButton(service_text, callback_data=f"service_{service[0]}"))
        
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="services"))
        bot.edit_message_text(f"<b>🛒 خدمات {category}:</b>", call.message.chat.id, call.message.id, 
                            parse_mode='HTML', reply_markup=keyboard)
    
    elif data.startswith("service_"):
        service_id = int(data.split("service_")[1])
        cursor.execute('''SELECT name, price_per_1000, min_quantity, max_quantity, note, api_service_id 
                         FROM services WHERE id = ?''', (service_id,))
        service = cursor.fetchone()
        
        if service:
            name, price, min_q, max_q, note, api_id = service
            user_states[user_id] = {
                'state': 'waiting_quantity',
                'service_id': service_id,
                'service_name': name,
                'price_per_1000': price,
                'min_quantity': min_q,
                'max_quantity': max_q,
                'api_service_id': api_id,
                'note': note
            }
            
            msg = f"""<b>🛍️ تفاصيل الخدمة:</b>

📝 <b>{name}</b>
💰 السعر: {price} نقطة / 1000
📏 الحد الأدنى: {min_q}
📏 الحد الأقصى: {max_q}

{'> ملاحظة: ' + note if note else ''}

<b>💬 أرسل الكمية المطلوبة:</b>"""
            
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="services"))
            
            bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "balance":
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        balance = cursor.fetchone()[0]
        bot.answer_callback_query(call.id, f"💰 رصيدك: {balance:,} نقطة", show_alert=True)
    
    elif data == "my_orders":
        cursor.execute('''SELECT order_id, service_name, quantity, status, created_at 
                         FROM orders WHERE user_id = ? ORDER BY order_id DESC LIMIT 10''', (user_id,))
        orders = cursor.fetchall()
        
        if orders:
            msg = "<b>📦 آخر طلباتك:</b>\n\n"
            for order in orders:
                status_emoji = {"pending": "⏳", "In progress": "⚡", "Partial": "↕️", "Completed": "✅", "Cancelled": "❌"}
                emoji = status_emoji.get(order[3], "❓")
                msg += f"{emoji} <code>#{order[0]}</code> | {order[1][:30]}...\n   الكمية: {order[2]:,}\n   الحالة: {order[3]}\n   {order[4][:10]}\n\n"
        else:
            msg = "📭 لم تقم بأي طلبات بعد"
        
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔍 تتبع طلب", callback_data="track_order"))
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="back_to_start"))
        
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "track_order":
        user_states[user_id] = {'state': 'track_order'}
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="my_orders"))
        bot.edit_message_text("<b>🔍 أرسل ID الطلب لتتبعه:</b>", call.message.chat.id, call.message.id, 
                            parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "add_balance":
        msg = """
<b>💳 طرق شحن الرصيد:</b>

💵 <b>الأسعار:</b>
$1 = 1,000 نقطة
$5 = 5,000 نقطة  
$10 = 10,000 نقطة
$20 = 20,000 نقطة

<b>📞 تواصل مع الدعم للشحن:</b>
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("💬 الدعم الفني", url="https://t.me/Helpfolo"))
        keyboard.add(InlineKeyboardButton("↩️ رجوع", callback_data="back_to_start"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, parse_mode='HTML', reply_markup=keyboard)
    
    elif data == "use_code":
        user_states[user_id] = {'state': 'use_promo_code'}
        bot.edit_message_text("<b>🎟️ أرسل كود الخصم:</b>", call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "back_to_start":
        bot.delete_message(call.message.chat.id, call.message.id)
        start(call.message)
    
    # أوامر المطور
    elif data == "update_services_api":
        bot.answer_callback_query(call.id, "جاري التحديث...")
        if update_services_from_api():
            bot.edit_message_text("✅ تم تحديث الخدمات من KD Media API بنجاح!", 
                                call.message.chat.id, call.message.id, parse_mode='HTML')
        else:
            bot.edit_message_text("❌ فشل في تحديث الخدمات. تحقق من مفتاح API", 
                                call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "check_api_balance":
        balance_response = api_handler.get_balance()
        if 'error' not in balance_response:
            balance = balance_response.get('balance', 'غير معروف')
            bot.edit_message_text(f"✅ رصيد API: <b>{balance} {balance_response.get('currency', 'USD')}</b>", 
                                call.message.chat.id, call.message.id, parse_mode='HTML')
        else:
            bot.edit_message_text(f"❌ خطأ: {balance_response.get('error', 'غير معروف')}", 
                                call.message.chat.id, call.message.id, parse_mode='HTML')
    
    elif data == "check_order":
        user_states[user_id] = {'state': 'dev_check_order'}
        bot.edit_message_text("<b>🔍 أرسل ID الطلب (من قاعدة البيانات):</b>", 
                            call.message.chat.id, call.message.id, parse_mode='HTML')

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if user_id not in user_states:
        return
    
    state = user_states[user_id].get('state')
    
    if state == 'waiting_quantity':
        try:
            quantity = int(text)
            service_data = user_states[user_id]
            
            if quantity < service_data['min_quantity']:
                bot.reply_to(message, f"❌ الكمية الحد الأدنى: {service_data['min_quantity']}")
                return
            if quantity > service_data['max_quantity']:
                bot.reply_to(message, f"❌ الكمية الحد الأقصى: {service_data['max_quantity']}")
                return
            
            total_price = (quantity / 1000) * service_data['price_per_1000']
            
            cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            balance = cursor.fetchone()[0]
            
            if balance < total_price:
                bot.reply_to(message, f"❌ رصيدك غير كافي!\n💰 مطلوب: {total_price:.0f} نقطة\n💳 رصيدك: {balance:,} نقطة")
                return
            
            # حفظ الكمية وطلب الرابط
            service_data['quantity'] = quantity
            service_data['total_price'] = total_price
            service_data['state'] = 'waiting_link'
            
            bot.reply_to(message, f"""
<b>💰 التكلفة: {total_price:.0f} نقطة</b>
📏 الكمية: {quantity:,}

🔗 <b>أرسل الرابط الآن:</b>
<i>تأكد أن الحساب/القناة عامة</i>
            """, parse_mode='HTML')
            
        except ValueError:
            bot.reply_to(message, "❌ أرسل رقم صحيح للكمية")
    
    elif state == 'waiting_link':
        link = text
        service_data = user_states[user_id]
        
        # خصم الرصيد
        cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', 
                      (service_data['total_price'], user_id))
        cursor.execute('UPDATE users SET total_orders = total_orders + 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        
        # إرسال الطلب للـ API
        api_response = api_handler.add_order(
            service_data['api_service_id'],
            link,
            service_data['quantity']
        )
        
        # حفظ الطلب
        cursor.execute('''
            INSERT INTO orders (user_id, service_name, api_service_id, quantity, link, price, 
                              status, api_order_id, api_response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            service_data['service_name'],
            service_data['api_service_id'],
            service_data['quantity'],
            link,
            service_data['total_price'],
            'pending',
            api_response.get('order') if 'order' in api_response else None,
            str(api_response)
        ))
        order_id = cursor.lastrowid
        conn.commit()
        
        # إرسال تأكيد للمستخدم
        new_balance = service_data['balance'] - service_data['total_price']
        if 'order' in api_response:
            success_msg = f"""
✅ <b>تم إرسال الطلب بنجاح!</b>

🆔 <b>ID الطلب:</b> <code>{order_id}</code>
🛠️ <b>الخدمة:</b> {service_data['service_name']}
📏 <b>الكمية:</b> {service_data['quantity']:,}
🔗 <b>الرابط:</b> <code>{link}</code>
💰 <b>التكلفة:</b> {service_data['total_price']:.0f} نقطة
💳 <b>رصيدك الجديد:</b> {new_balance:,} نقطة

📊 <b>API Order ID:</b> <code>{api_response['order']}</code>
            """
        else:
            # استرجاع الرصيد في حالة الخطأ
            cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', 
                          (service_data['total_price'], user_id))
            conn.commit()
            
            error_msg = api_response.get('error', 'خطأ غير معروف')
            success_msg = f"""
❌ <b>فشل في إرسال الطلب</b>

🆔 <b>ID:</b> <code>{order_id}</code>
🚫 <b>الخطأ:</b> {error_msg}
🔗 <b>الرابط:</b> <code>{link}</code>

💰 تم استرجاع {service_data['total_price']:.0f} نقطة إلى رصيدك
            """
        
        bot.reply_to(message, success_msg, parse_mode='HTML')
        
        # إرسال تفاصيل الطلب للمجموعة
        try:
            username = message.from_user.username or "غير محدد"
            group_msg = f"""
🚨 <b>طلب جديد #{order_id}</b>

👤 <b>المستخدم:</b> <code>{user_id}</code> (@{username})
🛠️ <b>الخدمة:</b> {service_data['service_name']}
📏 <b>الكمية:</b> {service_data['quantity']:,}
🔗 <b>الرابط:</b> <code>{link}</code>
💰 <b>السعر:</b> {service_data['total_price']:.0f} نقطة

<b>📡 رد الـ API:</b>
<code>{str(api_response)}</code>

{'✅ نجح' if 'order' in api_response else '❌ فشل'}
            """
            bot.send_message(GROUP_ID, group_msg, parse_mode='HTML')
        except:
            print("فشل إرسال إشعار للمجموعة")
        
        del user_states[user_id]
    
    elif state == 'use_promo_code':
        code = text.upper()
        cursor.execute('SELECT value, used FROM codes WHERE code = ?', (code,))
        code_data = cursor.fetchone()
        
        if code_data and code_data[1] == 0:
            value = code_data[0]
            cursor.execute('UPDATE users SET balance = balance + ?, total_charged = total_charged + ? WHERE user_id = ?', 
                          (value, value, user_id))
            cursor.execute('UPDATE codes SET used = 1 WHERE code = ?', (code,))
            conn.commit()
            bot.reply_to(message, f"✅ تم إضافة <b>{value:,}</b> نقطة بنجاح!", parse_mode='HTML')
        else:
            bot.reply_to(message, "❌ الكود غير صحيح أو مستخدم", parse_mode='HTML')
        del user_states[user_id]
    
    elif state == 'track_order':
        try:
            order_id = int(text)
            cursor.execute('SELECT * FROM orders WHERE order_id = ? AND user_id = ?', (order_id, user_id))
            order = cursor.fetchone()
            
            if order:
                api_order_id = order[8]  # api_order_id
                status = order[7]  # status
                
                # تحديث الحالة من API إذا كان لدينا API order ID
                if api_order_id:
                    api_status = api_handler.get_order_status(int(api_order_id))
                    if 'error' not in api_status:
                        new_status = api_status.get('status', 'Unknown')
                        cursor.execute('UPDATE orders SET status = ? WHERE order_id = ?', (new_status, order_id))
                        conn.commit()
                        status = new_status
                
                bot.reply_to(message, f"""
<b>🔍 تفاصيل الطلب #{order_id}</b>

🛠️ {order[2]}  # الخدمة
📏 {order[4]:,}  # الكمية
🔗 <code>{order[5]}</code>  # الرابط
💰 {order[6]} نقطة  # السعر
📊 <b>الحالة:</b> {status}

API ID: <code>{api_order_id or 'غير متوفر'}</code>
                """, parse_mode='HTML')
            else:
                bot.reply_to(message, "❌ طلب غير موجود", parse_mode='HTML')
        except:
            bot.reply_to(message, "❌ أرسل ID صحيح", parse_mode='HTML')
        del user_states[user_id]

# نسخ احتياطي تلقائي
def backup_thread():
    while True:
        try:
            with open('bot_database.db', 'rb') as f:
                bot.send_document(DEVELOPER_ID, f, caption=f"📦 نسخ احتياطي - {time.strftime('%Y-%m-%d %H:%M')}")
        except:
            pass
        time.sleep(86400)  # كل 24 ساعة

# بدء البوت
if __name__ == "__main__":
    print("🚀 بدء تشغيل بوت KD Media SMM...")
    
    # اختبار الـ API
    print("🧪 اختبار اتصال KD Media API...")
    if api_handler.test_api_connection():
        print("✅ API يعمل بشكل صحيح")
        update_services_from_api()
    else:
        print("⚠️ تحذير: مشكلة في الـ API")
    
    # بدء النسخ الاحتياطي
    threading.Thread(target=backup_thread, daemon=True).start()
    
    # تشغيل البوت
    while True:
        try:
            print("🤖 البوت يعمل...")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(10)