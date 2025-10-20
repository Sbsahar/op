# funding.py - الملف المنفصل لإدارة التمويل والتجميع من الانضمام للقنوات
# funding.py
# التعديلات: إضافة imports لـ threading, time, و bot

import sqlite3
import threading
import time
from datetime import datetime, timedelta
from tstop1 import bot  # استيراد bot من الملف الرئيسي (tstop.py أو tstop1.py)

# ... (الباقي من الكود كما هو، بما في ذلك الدوال والخيوط)

conn = sqlite3.connect('bot_database.db', check_same_thread=False)

# إنشاء جداول التمويل إذا لم تكن موجودة
def create_funding_tables():
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fundings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        channel_username TEXT,
        requested_members INTEGER,
        remaining_members INTEGER,
        status TEXT DEFAULT 'active',  -- active, completed, cancelled
        created_at TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS funding_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        channel_username TEXT,
        requested_members INTEGER,
        created_at TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_join_history (
        user_id INTEGER,
        funding_id INTEGER,
        join_date TEXT,
        PRIMARY KEY (user_id, funding_id)
    )''')
    conn.commit()

create_funding_tables()

# إضافة طلب تمويل
def add_funding_request(user_id, channel_username, requested_members):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM fundings WHERE status = "active"',)
    active_count = cursor.fetchone()[0]
    if active_count >= 20:
        # إضافة إلى الطابور
        now = datetime.now().isoformat()
        cursor.execute('INSERT INTO funding_queue (user_id, channel_username, requested_members, created_at) VALUES (?, ?, ?, ?)', (user_id, channel_username, requested_members, now))
        conn.commit()
        return "queue"
    else:
        # إضافة مباشرة
        cost = requested_members * 8
        cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (cost, user_id))
        now = datetime.now().isoformat()
        cursor.execute('INSERT INTO fundings (user_id, channel_username, requested_members, remaining_members, created_at) VALUES (?, ?, ?, ?, ?)', (user_id, channel_username, requested_members, requested_members, now))
        conn.commit()
        return "added"

# الحصول على القناة التالية للمستخدم (غير مشترك، لم ينضم مؤخرًا)
def get_next_channel_for_user(user_id):
    cursor = conn.cursor()
    cursor.execute('''SELECT f.id, f.channel_username 
                      FROM fundings f
                      WHERE f.remaining_members > 0 AND f.status = 'active'
                      AND NOT EXISTS (SELECT 1 FROM user_join_history h WHERE h.user_id = ? AND h.funding_id = f.id AND h.join_date > ?)
                      LIMIT 1''', (user_id, (datetime.now() - timedelta(weeks=1)).isoformat()))
    result = cursor.fetchone()
    if result:
        return {'id': result[0], 'username': result[1]}
    return None

# التحقق من الاشتراك وإضافة نقاط
def check_and_award_join(user_id, funding_id):
    cursor = conn.cursor()
    cursor.execute('SELECT channel_username FROM fundings WHERE id = ?', (funding_id,))
    channel_username = cursor.fetchone()[0]
    try:
        member = bot.get_chat_member(f'@{channel_username}', user_id)
        if member.status not in ['left', 'kicked'] and not cursor.execute('SELECT 1 FROM user_join_history WHERE user_id = ? AND funding_id = ?', (user_id, funding_id)).fetchone():
            cursor.execute('UPDATE users SET balance = balance + 5 WHERE user_id = ?', (user_id,))
            cursor.execute('UPDATE fundings SET remaining_members = remaining_members - 1 WHERE id = ?', (funding_id,))
            now = datetime.now().isoformat()
            cursor.execute('INSERT INTO user_join_history (user_id, funding_id, join_date) VALUES (?, ?, ?)', (user_id, funding_id, now))
            conn.commit()
            # التحقق إذا انتهى التمويل
            cursor.execute('SELECT remaining_members, user_id FROM fundings WHERE id = ?', (funding_id,))
            remaining, owner_id = cursor.fetchone()
            if remaining <= 0:
                cursor.execute('UPDATE fundings SET status = "completed" WHERE id = ?', (funding_id,))
                conn.commit()
                bot.send_message(owner_id, f"<b>تم الانتهاء من تمويل قناتك @{channel_username} بنجاح ✅!\nلا تقم بإزالة البوت من المشرفين لتجنب الخصم.</b>", parse_mode='HTML')
            return True
    except:
        pass
    return False

# الحصول على التمويلات النشطة
def get_active_fundings():
    cursor = conn.cursor()
    cursor.execute('SELECT id, channel_username FROM fundings WHERE status = "active"')
    return [{'id': row[0], 'channel_username': row[1]} for row in cursor.fetchall()]

# تفاصيل تمويل
def get_funding_details(funding_id):
    cursor = conn.cursor()
    cursor.execute('SELECT channel_username, requested_members, remaining_members, user_id FROM fundings WHERE id = ?', (funding_id,))
    result = cursor.fetchone()
    if result:
        return {'channel_username': result[0], 'requested_members': result[1], 'remaining_members': result[2], 'user_id': result[3]}
    return None

# إزالة تمويل
def remove_funding(funding_id):
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, channel_username FROM fundings WHERE id = ?', (funding_id,))
    result = cursor.fetchone()
    if result:
        owner_id, channel_username = result
        cursor.execute('UPDATE fundings SET status = "cancelled" WHERE id = ?', (funding_id,))
        cursor.execute('DELETE FROM user_join_history WHERE funding_id = ?', (funding_id,))
        conn.commit()
        bot.send_message(owner_id, f"<b>تم حذف قناتك @{channel_username} من التمويل بواسطة المطور ❌.\nالسبب: مخالفة لسياسة البوت.</b>", parse_mode='HTML')
        return True
    return False

# خيط لفحص إزالة البوت من المشرفين (تشغيل دوري كل ساعة)
def check_admin_status_thread():
    while True:
        cursor = conn.cursor()
        cursor.execute('SELECT id, channel_username, user_id FROM fundings WHERE status = "active"')
        fundings = cursor.fetchall()
        for funding in fundings:
            funding_id, channel_username, owner_id = funding
            try:
                admins = bot.get_chat_administrators(f'@{channel_username}')
                bot_id = bot.get_me().id
                is_admin = any(admin.user.id == bot_id and admin.can_invite_users for admin in admins)
                if not is_admin:
                    remove_funding(funding_id)
                    bot.send_message(owner_id, f"<b>تم إلغاء تمويل قناتك @{channel_username} لأن البوت تم إزالته من المشرفين ❌.</b>", parse_mode='HTML')
            except:
                pass
        time.sleep(3600)  # كل ساعة

threading.Thread(target=check_admin_status_thread).start()

# خيط لمعالجة الطابور (إضافة من الطابور عند توفر مساحة)
def process_queue_thread():
    while True:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM fundings WHERE status = "active"')
        active_count = cursor.fetchone()[0]
        if active_count < 20:
            cursor.execute('SELECT id, user_id, channel_username, requested_members FROM funding_queue ORDER BY created_at ASC LIMIT 1')
            queue_item = cursor.fetchone()
            if queue_item:
                queue_id, user_id, channel_username, requested_members = queue_item
                add_funding_request(user_id, channel_username, requested_members)
                cursor.execute('DELETE FROM funding_queue WHERE id = ?', (queue_id,))
                conn.commit()
                bot.send_message(user_id, f"<b>تم إضافة قناتك @{channel_username} إلى التمويل من الطابور ✅!</b>", parse_mode='HTML')
        time.sleep(600)  # كل 10 دقائق

threading.Thread(target=process_queue_thread).start()