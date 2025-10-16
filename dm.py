# ⚠️ حقوق محفوظة ¦ @avetaar
# 🔄 مسموح بالتحويل مع الحفاظ على حقوقي فقط
import requests
import json
import time
import os
import random
import base64
import re
import datetime
from urllib.parse import urlparse

# --- START OF FILE دعمكم.py ---

Token = "7524766252:AAFfFAFCMrtloJeCFI_4auUD_ahvuyaONzQ"  # توكنك
admin = 6789179634  # ايديك
API_KEY = Token

def bot(method, datas={}):
    Saied_Botate = f"https://api.telegram.org/bot{API_KEY}/{method}"
    saied_botate = None
    if datas:
        boundary = '----WebKitFormBoundary' + ''.join(random.sample('0123456789abcdef', 16))
        saied_botate = buildMultipartData(datas, boundary)
        headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
        try:
            response = requests.post(Saied_Botate, data=saied_botate, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    else:
        try:
            response = requests.get(Saied_Botate)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

def buildMultipartData(data, boundary):
    SaiedData = []
    for key, value in data.items():
        if isinstance(value, tuple) and len(value) == 3:  # (filename, content, mimetype)
            SaiedData.append(f"--{boundary}")
            SaiedData.append(f'Content-Disposition: form-data; name="{key}"; filename="{value[0]}"')
            SaiedData.append(f'Content-Type: {value[2]}')
            SaiedData.append('')
            SaiedData.append(value[1])
        else:
            SaiedData.append(f"--{boundary}")
            SaiedData.append(f'Content-Disposition: form-data; name="{key}"')
            SaiedData.append('')
            SaiedData.append(str(value))
    SaiedData.append(f"--{boundary}--")
    return "\r\n".join(SaiedData).encode('utf-8')

# نهاية الفاكشن وبداية لوحة الادمن
def get_update(offset=None):
    try:
        params = {'timeout': 100, 'offset': offset}
        response = requests.get(f"https://api.telegram.org/bot{API_KEY}/getUpdates", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching updates: {e}")
        return None

def process_update(update):
    global Token, admin, API_KEY # Ensure these are accessible globally

    message = update.get('message')
    callback_query = update.get('callback_query')

    chat_id = None
    from_id = None
    name = None
    user = None
    message_id = None
    text = None

    if message:
        chat_id = message['chat']['id']
        from_id = message['from']['id']
        name = message['from'].get('first_name')
        user = message['from'].get('username')
        message_id = message['message_id']
        text = message.get('text')
    elif callback_query:
        chat_id = callback_query['message']['chat']['id']
        from_id = callback_query['from']['id']
        name = callback_query['from']['first_name']
        message_id = callback_query['message']['message_id']
        data = callback_query['data']
    else:
        return

    os.makedirs("data", exist_ok=True)
    os.makedirs("sudo", exist_ok=True)
    os.makedirs("RSHQ", exist_ok=True)

    def read_file(filename, default=""):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return default

    def write_file(filename, content):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    msg = read_file("msg.php")
    forward = read_file("forward.php")
    midea = read_file("midea.php")
    inlin = read_file("inlin.php")
    photoi = read_file("photoi.php")
    upq = read_file("up.php")
    skor = read_file("skor.php", "معطل ⚠️")
    channel = read_file("link.php")
    link = read_file("link2.php")

    ch = channel.strip() if channel else ""

    if message and ch:
        join_status = bot('getChatMember', {'chat_id': ch, 'user_id': from_id})
        if join_status and join_status.get('result', {}).get('status') in ['left', 'kicked'] or join_status and join_status.get('error_code') == 400:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"🤍| عذرا عزيزي\n🕊| عليك الاشتراك بقناة البوت لتتمكن من استخدامه\n\n- ({link})\n\n🌼| اشترك ثم ارسل /start",
                'parse_mode': "Markdown",
                'disable_web_page_preview': True,
            })
            return

    uuser = read_file("uuser.php")
    if message and uuser and uuser != "on":
        join_status_uuser = bot('getChatMember', {'chat_id': uuser, 'user_id': from_id})
        if join_status_uuser and join_status_uuser.get('result', {}).get('status') in ['left', 'kicked'] or join_status_uuser and join_status_uuser.get('error_code') == 400:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"🤍| عذرا عزيزي\n🕊| عليك الاشتراك بقناة البوت لتتمكن من استخدامه\n\n- {uuser}\n\n🌼| اشترك ثم ارسل /start",
            })
            return

    users = []
    try:
        with open("arslan.json", 'r', encoding='utf-8') as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        pass

    if message:
        if str(from_id) not in users:
            with open("arslan.json", 'a', encoding='utf-8') as f:
                f.write(str(from_id) + "\n")
            users.append(str(from_id))

    arslan09 = {}
    try:
        with open("arslan09.json", 'r', encoding='utf-8') as f:
            arslan09 = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        arslan09 = {'sudoarr': [], 'addmessage': 0, 'messagee': 0}

    suodo = arslan09.get('sudoarr', [])
    al = arslan09.get('addmessage', 0)
    ab = arslan09.get('messagee', 0)
    xll = al + ab

    if message and from_id != admin:
        arslan09['messagee'] = arslan09.get('messagee', 0) + 1
        write_file("arslan09.json", json.dumps(arslan09, indent=4, ensure_ascii=False))
    if message and from_id == admin:
        arslan09['addmessage'] = arslan09.get('addmessage', 0) + 1
        write_file("arslan09.json", json.dumps(arslan09, indent=4, ensure_ascii=False))

    all_users_count = len(users)

    adminss = []
    try:
        with open("ad.json", 'r', encoding='utf-8') as f:
            adminss = f.read().splitlines()
    except FileNotFoundError:
        pass

    k088 = read_file("data/k088.txt")
    q1 = read_file("data/q1.txt")
    q2 = read_file("q2.txt")
    q3 = read_file("data/q3.txt")
    q4 = read_file("q4.txt")
    q5 = read_file("data/q5.txt")
    aralikan = read_file("q6.txt")

    if message:
        if str(admin) not in adminss:
            bot('sendmessage', {
                'chat_id': admin,
                'text': "تم تحديث القائمه /start",
            })
            with open("ad.json", 'a', encoding='utf-8') as f:
                f.write(str(admin) + "\n")
            adminss.append(str(admin))

    d = time.strftime('%a')
    today_users = []
    try:
        with open(f"{d}.txt", 'r', encoding='utf-8') as f:
            today_users = f.read().splitlines()
    except FileNotFoundError:
        pass

    if d == "Sat":
        if os.path.exists("Fri.txt"): os.remove("Fri.txt")
    if d == "Sun":
        if os.path.exists("Sat.txt"): os.remove("Sat.txt")
    if d == "Mon":
        if os.path.exists("Sun.txt"): os.remove("Sun.txt")
    if d == "Tue":
        if os.path.exists("Mon.txt"): os.remove("Mon.txt")
    if d == "Wed":
        if os.path.exists("Tue.txt"): os.remove("Tue.txt") # Corrected typo "The" to "Tue"
    if d == "Thu":
        if os.path.exists("Wed.txt"): os.remove("Wed.txt")
    if d == "Fri":
        if os.path.exists("Thu.txt"): os.remove("Thu.txt")

    if message and str(from_id) not in today_users:
        with open(f"{d}.txt", 'a', encoding='utf-8') as f:
            f.write(str(from_id) + "\n")
        today_users.append(str(from_id))

    id = from_id
    if message:
        if user:
            user = f"@{user}"
        else:
            user = "بلا معرف"

    if message and text == "/start" and str(from_id) not in users:
        bot('sendmessage', {
            'chat_id': admin,
            'text': f"٭ تم دخول شخص جديد الى البوت الخاص بك 🤍\n\n• معلومات العضو الجديد .\n                 •--•\n• الاسم : {name}\n• المعرف : {user}\n• الايدي : {id}\n                  •--•\n• عدد الاعضاء الكلي : {all_users_count}",
        })

    bot_status = read_file("bot.txt")

    if message and text == "/admin" and str(from_id) in adminss:
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "✰ ⁞ اهلا بك مطوري اليك لوحة التحكم الخاصه بك 🤍\n  ✰ ⁞ لا تنسئ الصلاة علئ النبي 🤍",
            'parse_mode': "Markdown",
            'reply_markup': json.dumps({
                "inline_keyboard": [
                    [{"text": "- قفل البوت .", "callback_data": "abcd"}, {"text": "- فتح البوت .", "callback_data": "abcde"}],
                    [{"text": "- اعضاء البوت .", "callback_data": "userd"}],
                    [{"text": "- تفعيل التنبيه .", "callback_data": "ont"}, {"text": "- تعطيل التنبيه .", "callback_data": "oft"}],
                    [{"text": "- قسم الاذاعةه .", "callback_data": "for"}],
                    [{"text": "- قائمةه الاشتراك .", "callback_data": "channel"}, {"text": f"- الاشتراك ({skor}) .", "callback_data": "off"}],
                    [{"text": "- نسخة احتياطيةه .", "callback_data": "file"}, {"text": "- رفع النسخةه .", "callback_data": "up"}],
                    [{"text": "- الاحصائيات .", "callback_data": "pannel"}, {"text": "- قسم الادمن .", "callback_data": "lIllarslan"}],
                    [{"text": "- التعديلات .", "callback_data": "xxxtentacionllllo"}],
                    [{"text": "- كليشةه /start .", "callback_data": "editstart"}],
                ]
            })
        })

    # رفع ادمن
    if callback_query and data == "lIllarslan":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "اهلا بك مطوري في قسم رفع ادمن اخر",
            'parse_mode': "Markdown",
            'reply_markup': json.dumps({
                "inline_keyboard": [
                    [{"text": "- رفع ادمن.", "callback_data": "adl"}],
                    [{"text": "- اخر الادمن.", "callback_data": "addmin"}],
                    [{"text": "- حذف الادمنيه.", "callback_data": "delateaddmin"}],
                ]
            })
        })

    if callback_query and data == "adl":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "\nقم بارسال ايدي العضو\n",
        })
        write_file("data/k088.txt", "k088")

    if message and text and text != "/start" and k088 == "k088" and str(text) not in adminss:
        write_file("data/k088.txt", "none")
        with open("ad.json", 'a', encoding='utf-8') as f:
            f.write(str(text) + "\n")
        adminss.append(str(text))
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "تم رفع العضو",
        })
        bot('sendmessage', {
            'chat_id': int(text),
            'text': "تم رفعك ادمن في البوت",
        })
    elif message and text and text != "/start" and k088 == "k088" and str(text) in adminss:
        write_file("data/k088.txt", "none")
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "العضو ادمن بالفعل",
        })

    if callback_query and data == "addmin":
        last_five_admins = adminss[-6:-1][::-1] if len(adminss) > 1 else []
        admin_list_text = "\n".join([f"{i + 1} - {admin_id}" for i, admin_id in enumerate(last_five_admins)])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"اخر خمس ادمنيه :\n{admin_list_text}\n",
            'parse_mode': "Markdown",
            'reply_markup': json.dumps({
                "inline_keyboard": [
                    [{"text": "- الصفحه الرئيسيه.", "callback_data": "rshqG"}],
                ]
            })
        })

    if callback_query and data == "delateaddmin" and chat_id == admin:
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "هل انت متاكد من الحذف",
            'parse_mode': "MarkDown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'لا', 'callback_data': "rshqG"}],
                    [{'text': 'نعم', 'callback_data': "yesaarsslan"}],
                ]
            })
        })

    if callback_query and data == "yesaarsslan":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "تم حذف الادمنيه",
            'parse_mode': "MarkDown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'الصفحه الرئيسيه', 'callback_data': "rshqG"}],
                ]
            })
        })
        if os.path.exists("ad.json"): os.remove("ad.json")

    if callback_query and data == "abcde":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "- اهلا بك عزيزي\n- تم فتح البوت\n- /start",
            'parse_mode': "MarkDown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'الصفحه الرئيسيه', 'callback_data': "rshqG"}],
                ]
            })
        })
        write_file("bot.txt", "مفتوح")

    if callback_query and data == "abcd":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "- اهلا بك عزيزي\n- تم قفل البوت\n- /start ",
            'parse_mode': "MarkDown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'الصفحه الرئيسيه', 'callback_data': "rshqG"}],
                ]
            })
        })
        write_file("bot.txt", "متوقف")

    if message and text == "/start" and bot_status == "متوقف" and chat_id != admin:
        bot("sendmessage", {
            "chat_id": chat_id,
            "text": "عذرا البوت يخضع للتحديث الان",
        })

    if callback_query and data == "userd":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"اهلا بك عزيزي الادمن\n عدد الاعضاء : ( {all_users_count} )",
            'parse_mode': "MarkDown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'الصفحه الرئيسيه', 'callback_data': "rshqG"}],
                ]
            })
        })

    if callback_query and data == 'ont':
        write_file("ont.php", "on")
        bot('answerCallbackQuery', {
            'callback_query_id': update['callback_query']['id'],
            'text': "مرحبا عزيزي\n تم تفعيل الاشعارات في البوت\n➖➖➖➖➖➖➖➖",
            'show_alert': True
        })

    if callback_query and data == 'oft':
        write_file("ont.php", "off")
        bot('answerCallbackQuery', {
            'callback_query_id': update['callback_query']['id'],
            'text': "مرحبا عزيزي\n⚠ تم تعطيل الاشعارات في البوت\n➖➖➖➖➖➖➖➖",
            'show_alert': True
        })

    ont = read_file("ont.php")
    if ont == "on":
        if message and from_id != admin:
            bot('ForwardMessage', {
                'chat_id': admin,
                'from_chat_id': chat_id,
                'message_id': message_id,
            })

    if callback_query and data == "for":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n قم باختيار ما يناسبك",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "اذاعه صورة ", "callback_data": "photoi"}],
                    [{"text": "اذاعه رسالة ", "callback_data": "msg"}, {"text": "اذاعه توجيه ", "callback_data": "forward"}],
                    [{"text": "اذاعه ميديا ", "callback_data": "midea"}, {"text": "اذاعه انلاين ", "callback_data": "inline"}],
                    [{"text": "رجوع ", "callback_data": "rshqG"}],
                ]
            })
        })

    if callback_query and data == "msg":
        write_file("msg.php", "on")
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n قم بأرسال رسالتك لتحويلها لجميع المشتركين",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "الغاء", "callback_data": "rshqG"}],
                ]
            })
        })

    if message and msg == "on":
        for user_id in users:
            if user_id:
                bot('sendmessage', {
                    'chat_id': user_id,
                    'text': text,
                })
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': f"حسنا عزيزي\n تم عمل اذاعه بنجاح\n الى ( {all_users_count} ) مشترك",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "رجوع ", "callback_data": "rshqG"}],
                ]
            })
        })
        if os.path.exists("msg.php"): os.remove("msg.php")

    if callback_query and data == "forward":
        write_file("forward.php", "on")
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n قم بأرسال رسالتك لتحويلها لجميع المشتركين على شكل توجيه",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "الغاء ", "callback_data": "rshqG"}],
                ]
            })
        })

    if message and forward == "on":
        for user_id in users:
            if user_id:
                bot('ForwardMessage', {
                    'chat_id': user_id,
                    'from_chat_id': chat_id,
                    'message_id': message_id,
                })
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': f"حسنا عزيزي\n تم عمل اذاعه توجيه بنجاح\n الى ( {all_users_count} ) مشترك",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "رجوع", "callback_data": "rshqG"}],
                ]
            })
        })
        if os.path.exists("forward.php"): os.remove("forward.php")

    if callback_query and data == "midea":
        write_file("midea.php", "on")
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n يمكنك استخدام جميع انوع الميديا ماعدى الصوره\n (ملصق - فيديو - بصمه - ملف صوتي - ملف - متحركه - جهة اتصال )",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "الغاء", "callback_data": "rshqG"}],
                ]
            })
        })

    if message and midea == "on":
        types = ['voice', 'audio', 'video', 'photo', 'contact', 'document', 'sticker']
        for msg_type in types:
            if message.get(msg_type):
                for user_id in users:
                    if user_id:
                        file_id_to_send = None
                        caption_to_send = message.get('caption')
                        if msg_type == 'photo': # Photo can be a list of different sizes
                            file_id_to_send = message[msg_type][0]['file_id']
                        elif isinstance(message.get(msg_type), dict):
                            file_id_to_send = message[msg_type]['file_id']
                        elif isinstance(message.get(msg_type), list) and message[msg_type]:
                            file_id_to_send = message[msg_type][0]['file_id'] # Take the first element if it's a list

                        if file_id_to_send:
                            bot(f'send{msg_type}', {
                                'chat_id': user_id,
                                'caption': caption_to_send,
                                msg_type: file_id_to_send
                            })
                if os.path.exists("midea.php"): os.remove("midea.php")
                break # Exit after processing the first media type found

    if callback_query and data == "photoi":
        write_file("photoi.php", "on")
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n قم بأرسال الصورة لنشرها لجميع المشتركين",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "الغاء ", "callback_data": "rshqG"}],
                ]
            })
        })

    if message and photoi == "on" and message.get('photo'):
        for user_id in users:
            if user_id:
                bot('sendphoto', {
                    'chat_id': user_id,
                    'photo': message['photo'][0]['file_id'],
                    'caption': message.get('caption'),
                })
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': f"حسنا عزيزي\n تم نشر الصورة بنجاح\n الى ( {all_users_count} ) مشترك",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "رجوع ", "callback_data": "rshqG"}],
                ]
            })
        })
        if os.path.exists("photoi.php"): os.remove("photoi.php")

    if callback_query and data == "inline":
        write_file("inlin.php", "on")
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n قم بتوجيه نص الانلاين لاقوم بنشره للمشتركين",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "الغاء", "callback_data": "rshqG"}],
                ]
            })
        })

    if message and inlin == "on" and (message.get('forward_from') or message.get('forward_from_chat')):
        for user_id in users:
            if user_id:
                bot('forwardmessage', {
                    'chat_id': user_id,
                    'from_chat_id': chat_id,
                    'message_id': message_id,
                })
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': f"حسنا عزيزي\n تم نشر الانلاين بنجاح\n الى ( {all_users_count} ) مشترك",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "رجوع ", "callback_data": "rshqG"}],
                ]
            })
        })
        if os.path.exists("inlin.php"): os.remove("inlin.php")

    if callback_query and data == "channel":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n قم بتحديد الامر لأتمكن من تنفيذه",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "قناة خاصة ", "callback_data": "link"}],
                    [{"text": "قناة عامة ", "callback_data": "user"}],
                    [{"text": "رجوع ", "callback_data": "rshqG"}],
                ]
            })
        })

    if callback_query and data == "link":
        write_file("link.php", "on")
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n قم برفع البوت ادمن في القناة\n ثم ارسل توجيه من القناة الى هنا",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "رجوع ", "callback_data": "rshqG"}],
                ]
            })
        })

    if message and channel == "on" and message.get('forward_from_chat'):
        channel_id = message['forward_from_chat']['id']
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "حسنا عزيزي\n قم الان بأرسال رابط القناة هنا",
        })
        write_file("link.php", str(channel_id))
        write_file("link2.php", "on")

    if message and link == "on":
        if re.match(r'^(.*)([Hh]ttp|[Hh]ttps|t.me)(.*)|([Hh]ttp|[Hh]ttps|t.me)(.*)|(.*)([Hh]ttp|[Hh]ttps|t.me)|(.*)[Tt]elegram.me(.*)|[Tt]elegram.me(.*)|(.*)[Tt]elegram.me|(.*)[Tt].me(.*)|[Tt].me(.*)|(.*)[Tt].me|(.*)telesco.me|telesco.me(.*)', text):
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "حسنا عزيزي\n تم تفعيل الاشتراك بنجاح",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{"text": "اتمام العملية", "callback_data": "rshqG"}],
                    ]
                })
            })
            write_file("link2.php", text)
            write_file("skor.php", "مفعل ✅")
        else:
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "عذرا عزيزي\n قم بأرسال الرابط بصورة صحيحه",
            })

    if callback_query and data == "user":
        write_file("uuser.php", "on")
        bot('editmessagetext', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n قم برفع البوت ادمن في القناة\n ثم ارسل يوزر القناة لتفعيل الاشتراك",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "رجوع ", "callback_data": "rshqG"}],
                ]
            })
        })

    if message and uuser == "on":
        if re.match(r'^(.*)@|@(.*)|(.*)@(.*)|(.*)#(.*)|#(.*)|(.*)#', text):
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "حسنا عزيزي\n تم تفعيل الاشتراك بنجاح",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{"text": "اتمام العملية ⏱", "callback_data": "rshqG"}],
                    ]
                })
            })
            write_file("skor.php", "مفعل ✅")
            write_file("uuser.php", text)
        else:
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "عذرا عزيزي\n قم بأرسال يوزر بصورة صحيحه",
            })

    if callback_query and skor == "معطل ⚠️" and data == 'off':
        bot('answerCallbackQuery', {
            'callback_query_id': update['callback_query']['id'],
            'text': "مرحبا عزيزي\n حالة الاشتراك الاجباري معطل\n قم بختيار - قائمةه الاشتراك .وقم بتفعيله",
            'show_alert': True
        })

    if callback_query and skor == "مفعل ✅" and data == 'off':
        bot('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n حالت الاشتراك الخاص بك مفعل\n هل انت متأكد من رغبتك في تعطيل الاشتراك",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [
                        {'text': 'نعم ', 'callback_data': 'yesde2'},
                        {'text': 'لا ', 'callback_data': 'rshqG'},
                    ]
                ]
            })
        })

    if callback_query and data == "yesde2":
        if os.path.exists("uuser.php"): os.remove("uuser.php")
        if os.path.exists("link.php"): os.remove("link.php")
        write_file("skor.php", "معطل ⚠️")
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n تم تعطيل الاشتراك في جميع القنواة\n يمكنك تفعيل الاشتراك لقناتك في مابعد",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "رجوع", "callback_data": "rshqG"}],
                ]
            })
        })

    bloktime = time.strftime('%I:%M:%S %p')
    if callback_query and data == "file":
        path = "arslan.json"
        if os.path.exists(path):
            with open(path, 'rb') as f:
                bot('senddocument', {
                    'chat_id': chat_id,
                    'document': (os.path.basename(path), f.read(), 'application/json'),
                    'caption': f"نسخة لمشتركينك\nوقت الارسال : ( {bloktime} )\nعدد المشتركين : ( {all_users_count} )\n",
                })
        else:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': "لا يوجد ملف مشتركين لتصديره.",
            })

    if callback_query and data == "up":
        bot('editmessagetext', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "حسنا عزيزي\n قم بأرسال ملف الاعضاء الان\n ارسل الملف بأسم : arslan.json",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "رجوع ", "callback_data": "rshqG"}],
                ]
            })
        })
        write_file("up.php", "on")

    if message and upq == "on" and message.get('document') and message['document']['file_name'] == "arslan.json":
        file_id = message['document']['file_id']
        file_info = bot('getFile', {'file_id': file_id})
        if file_info and file_info['ok']:
            file_path = file_info['result']['file_path']
            file_url = f"https://api.telegram.org/file/bot{API_KEY}/{file_path}"
            try:
                response = requests.get(file_url)
                response.raise_for_status()
                with open("arslan.json", 'wb') as f:
                    f.write(response.content)
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': f"* تم رفع الملف  : {message['document']['file_name']}*",
                    'parse_mode': "MarkDown",
                    'disable_web_page_preview': True,
                })
                if os.path.exists("up.php"): os.remove("up.php")
            except requests.exceptions.RequestException as e:
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': f"* حدث خطأ أثناء تنزيل الملف: {e}*",
                    'parse_mode': "MarkDown",
                    'disable_web_page_preview': True,
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{"text": "الغاء", "callback_data": "rshqG"}],
                        ]
                    })
                })
        else:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"* لايمكن رفع الملف  : {message['document']['file_name']}*",
                'parse_mode': "MarkDown",
                'disable_web_page_preview': True,
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{"text": "الغاء", "callback_data": "rshqG"}],
                    ]
                })
            })
    elif message and upq == "on" and (not message.get('document') or message['document']['file_name'] != "arslan.json"):
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "* لايمكن رفع الملف. يرجى إرسال ملف باسم arslan.json*",
            'parse_mode': "MarkDown",
            'disable_web_page_preview': True,
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "الغاء", "callback_data": "rshqG"}],
                ]
            })
        })

    if callback_query and data == "pannel":
        last_five_users = users[-6:-1][::-1] if len(users) > 1 else []
        users_list_text = "\n".join([f"▫️ {i + 1}- {user_id}" for i, user_id in enumerate(last_five_users)])

        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*اهلا بك في قسم - الاحصائيات . 📊\n--------------------------\n عدد اعضاء بوتك : {all_users_count}\n المتفاعلين اليوم  : {len(today_users)}\n عدد الرسائل المرسله : {arslan09['addmessage']}\n عدد الرسائل المستلمه : {arslan09['messagee']}\n مجموع الرسائل : {xll}\n--------------------------\n اخر خمس مشتركين :\n{users_list_text}\n--------------------------*",
            'parse_mode': "MarkDown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'الصفحه الرئيسيه', 'callback_data': "rshqG"}],
                ]
            })
        })

    if callback_query and data == "editstart":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "\nقم بارسال رسالة الاستارت الان\n",
        })
        write_file("data/q1.txt", "q1")

    if message and text and text != "/start" and q1 == "q1":
        write_file("data/q1.txt", "none")
        write_file("q2.txt", text)
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "تم التعين بنجاح",
        })

    if callback_query and data == 'rshqG':
        if os.path.exists("msg.php"): os.remove("msg.php")
        if os.path.exists("forward.php"): os.remove("forward.php")
        if os.path.exists("midea.php"): os.remove("midea.php")
        if os.path.exists("inlin.php"): os.remove("inlin.php")
        if os.path.exists("photoi.php"): os.remove("photoi.php")
        if os.path.exists("up.php"): os.remove("up.php")
        if os.path.exists("data/k088.txt"): write_file("data/k088.txt", "none") # Clear k088 state

        bot('editmessagetext', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "✰ ⁞ اهلا بك مطوري اليك لوحة التحكم الخاصه بك 🤍\n  ✰ ⁞ لا تنسئ الصلاة علئ النبي 🤍",
            'parse_mode': "Markdown",
            'reply_markup': json.dumps({
                "inline_keyboard": [
                    [{"text": "- قفل البوت .", "callback_data": "abcd"}, {"text": "- فتح البوت .", "callback_data": "abcde"}],
                    [{"text": "- اعضاء البوت .", "callback_data": "userd"}],
                    [{"text": "- تفعيل التنبيه .", "callback_data": "ont"}, {"text": "- تعطيل التنبيه .", "callback_data": "oft"}],
                    [{"text": "- قسم الاذاعةه .", "callback_data": "for"}],
                    [{"text": "- قائمةه الاشتراك .", "callback_data": "channel"}, {"text": f"- الاشتراك ({skor}) .", "callback_data": "off"}],
                    [{"text": "- نسخة احتياطيةه .", "callback_data": "file"}, {"text": "- رفع النسخةه .", "callback_data": "up"}],
                    [{"text": "- الاحصائيات .", "callback_data": "pannel"}, {"text": "- قسم الادمن .", "callback_data": "lIllarslan"}],
                    [{"text": "- التعديلات .", "callback_data": "xxxtentacionllllo"}],
                    [{"text": "- كليشةه /start .", "callback_data": "editstart"}],
                ]
            })
        })
    #----------------@Vl_HI-----------//

    # نهاية اللوحه وبداية الملف//
    usrbot_info = bot("getme")
    usrbot = usrbot_info['result']['username'] if usrbot_info and usrbot_info.get('ok') else "UNKNOWN_BOT"

    emoji = ["➡️", "🎟️", "↪️", "🔘", "🏠"]
    NamesBACK = f"رجوع {random.choice(emoji)}"

    def SETJSON(INPUT):
        if INPUT is not None and INPUT != "":
            f_path = "RSHQ/rshq.json"
            n_json = json.dumps(INPUT, indent=4, ensure_ascii=False)
            write_file(f_path, n_json)

    rshq = {}
    try:
        with open("RSHQ/rshq.json", 'r', encoding='utf-8') as f:
            rshq = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        rshq = {"mode": {}, "MGS": {}, "HACKER": {}, "HACK": {}, "3thu": [], "coin": {}, "mshark": {}, "thoiler": {}, "IDX": {}, "WSFV": {}, "S3RS": {}, "web": {}, "key": {}, "min_mix": {}, "SB1": {}, "SB2": {}, "=":{}, "3dd": {}, "tlbia": {}, "cointlb": {}, "s3rltlb": {}, "tp": {}, "coinn": None, "orders": {}, "order": {}, "ordn": {}, "sites": {}, "keys": {}, "tlby": {}, "coinss": {}, "bot_tlb": 0}

    BERO = {}
    try:
        with open(f"RSHQ/BERO_{usrbot}.json", 'r', encoding='utf-8') as f:
            BERO = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        BERO = {"BERO": {"send": {"uname": [], "add": []}}}


    timer = {}
    try:
        with open(f"RSHQ/TIMER_{usrbot}.json", 'r', encoding='utf-8') as f:
            timer = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        timer = {"TIME": {}, "acount": {}}

    if callback_query:
        # Check if from_id is in timer['TIME'] and if enough time has passed
        last_action_time_str = timer['TIME'].get(from_id)
        current_time_str = time.strftime("%H:%M:%S")

        if last_action_time_str:
            # Parse times to datetime objects for comparison
            FMT = "%H:%M:%S"
            last_action_time = datetime.datetime.strptime(last_action_time_str + ":00" if len(last_action_time_str) == 5 else last_action_time_str, FMT)
            current_time = datetime.datetime.strptime(current_time_str, FMT)

            # Calculate the time difference
            time_difference = current_time - last_action_time

            # If time_difference is negative, it means a day change occurred. Add 24 hours to compensate.
            if time_difference.total_seconds() < 0:
                time_difference += datetime.timedelta(days=1)

            if time_difference.total_seconds() < 3:
                if from_id != admin: # Allow admin to bypass flood control
                    bot('answerCallbackQuery', {
                        'callback_query_id': callback_query['id'],
                        'text': "انتظر 3 ثواني قبل ان تضغط امرأ آخر 😃",
                        'show_alert': True
                    })
                    return
        # Update time for the current action
        timer['TIME'][from_id] = current_time_str
        write_file(f"RSHQ/TIMER_{usrbot}.json", json.dumps(timer, indent=4, ensure_ascii=False))


    e = data.split("|") if callback_query else []
    e1_start = text.replace("/start", "") if message and text and text.startswith("/start") else ''

    if message and text and text.startswith("/start") and e1_start.isnumeric() and not re.search("#Bero#", text):
        rshq.setdefault('HACKER', {})[from_id] = "I"
        rshq.setdefault('HACK', {})[from_id] = e1_start.strip()
        SETJSON(rshq)

    sudo = admin

    if message and isinstance(chat_id, int) and chat_id < 0: # Checks if it's a group
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "👤] للأسف الشديد محاوله فاشله",
        })
        bot('leaveChat', {
            'chat_id': chat_id,
        })
        return

    chnl = rshq.get("sCh")
    Api_Tok = rshq.get("sToken")

    ARM = {}
    try:
        with open(f"RSHQ/{bot('getme')['result']['id']}.json", 'r', encoding='utf-8') as f: # Corrected file path
            ARM = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        ARM = {"BOTAPI_KEY": API_KEY}

    rsedi = {}
    if Api_Tok and rshq.get("sSite"):
        try:
            rsedi_response = requests.get(f"https://{rshq['sSite']}/api/v2?key={Api_Tok}&action=balance")
            rsedi_response.raise_for_status()
            rsedi = rsedi_response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching balance: {e}")
            rsedi = {"balance": 0, "currency": "N/A"}

    flos = rsedi.get("balance", 0)
    treqa = rsedi.get("currency", "N/A")

    b_const = "Bero"

    adm_keyboard = [
        [{"text": "✅ - إضافة وحذف أقسام وخدمات.", "callback_data": "xdmat"}],
        [{"text": "☑️ - اﺩنئ حد لتحويل رصيد", "callback_data": "sAKTHAR"}, {"text": "💰 - إضافة وخصم رصيد", "callback_data": "coins"}],
        [{"text": "📛 - تصفير رصيد عضو", "callback_data": "msfrn"}, {"text": "☢ - إنتاج كروت شحن", "callback_data": "hdiamk"}],
        [{"text": "♻️ - فتح قسم الرشق", "callback_data": "onrshq"}, {"text": "📛 - قفل قسم الرشق", "callback_data": "ofrshq"}],
        [{"text": "⚜ - تعيين توكن الموقع", "callback_data": "token"}, {"text": "🚾 - تعيين رابط الموقع", "callback_data": "SiteDomen"}],
        [{"text": "❇️ - تعيين قناة اثبات", "callback_data": "sCh"}, {"text": "🔰 - معلومات موقع الرشق", "callback_data": "infoRshq"}],
        [{"text": "❌ - قفل البوت", "callback_data": "abcd"}, {"text": "✅ - فتح البوت", "callback_data": "abcde"}],
        [{"text": "🌐 - قسم الاذاعة", "callback_data": "for"}],
        [{"text": "💠 - قائمة الاشتراك", "callback_data": "channel"}, {"text": f"Ⓜ️ - الاشتراك ({skor}) .", "callback_data": "off"}],
    ]
    adm = {'inline_keyboard': adm_keyboard}

    admnb = {
        'inline_keyboard': [
            [{'text': 'رجوع', 'callback_data': "rshqG"}],
        ]
    }

    admnvip = {
        'inline_keyboard': [
            [{'text': 'تعين كليشه شروط الاستخدام', 'callback_data': "settext"}],
            [{'text': 'تعين قناة لبوت', 'callback_data': "setcha"}, {'text': 'تعين اسم البوت', 'callback_data': "setname"}],
            [{'text': 'تعين كليشه شراء الرصيد', 'callback_data': "setbuy"}],
            [{'text': 'تعين كليشه الجوائز', 'callback_data': "setJa"}],
            [{'text': 'رجوع', 'callback_data': "rshqG"}],
        ]
    }

    if callback_query and data == "settext":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل الكليشه الان\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\n◉︙هذا القسم للمشتركين المدفوعين فقط\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })

    if callback_query and data == "msfrn":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل ايدي الشخص لتصفير نقاطه\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\n◉︙هذا القسم للمشتركين المدفوعين فقط\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })

    if message and text and rshq.get('mode', {}).get(from_id) == "msfrn":
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': f"*\nتم تصفير نقاط {text} \n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(admnb)
        })
        rshq.setdefault('coin', {})[text] = 0
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    if callback_query and data == "setname":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل اسم البوت الان .\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\n◉︙هذا القسم للمشتركين المدفوعين فقط\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })

    if callback_query and data == "setcha":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل يوزر القناة الان مع @\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\n◉︙هذا القسم للمشتركين المدفوعين فقط\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })

    if callback_query and data == "setbuy":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل كليشه شراء رصيد الان\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\n◉︙هذا القسم للمشتركين المدفوعين فقط\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })

    if callback_query and data == "setshare":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل عدد النقاط الان\nنقاط مشاركه رابط لدعوه، \n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\n◉︙هذا القسم للمشتركين المدفوعين فقط\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })

    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "setshare":
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "*\nتم تعيين عدد النقاط\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(admnb)
        })
        rshq['coinshare'] = int(text)
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "setbuy":
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "*\nتم تعيين الكليشه\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(admnb)
        })
        rshq['buy'] = text
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    chabot = rshq.get('cha')
    if chabot is None:
        chabot = "Vl_HI"

    if message and text and rshq.get('mode', {}).get(from_id) == "setname":
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "*\nتم تعيين اسم البوت\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(admnb)
        })
        rshq['namebot'] = text
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    nambot = rshq.get('namebot')
    if nambot is None:
        nambot = "خدمات @avetaar"

    if message and text and rshq.get('mode', {}).get(from_id) == "settext":
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "*\nتم تعيين الكليشه بنجاح\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(admnb)
        })
        rshq['KLISHA'] = text
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "setcha":
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': "*\nتم تعيين القناة بنجاح\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(admnb)
        })
        rshq['cha'] = text.replace("@", "")
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    AKTHAR = rshq.get('AKTHAR')
    if AKTHAR is None:
        AKTHAR = 20

    HDIAS = None
    mj = "❌"
    if rshq.get("HDIA") is None or rshq.get("HDIA") == "on":
        HDIAS = "الهديه اليوميه : 🎁"
        mj = "✅"

    if callback_query and data == "rshqG":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': f"*\n◉︙قسم الرشق \nيمنك اضافه او خصم رصيد\nيمكن قفل استقبال الرشق وفتحها\nيمكنك صنع هدايا \n*\n\nرصيدك في الموقع : *{flos}*\nالعمله : *{treqa}*\nاقل عدد لتحويل الرصيد : *{AKTHAR}*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(adm)
            })
            rshq.setdefault('mode', {})[from_id] = None
            SETJSON(rshq)

    if message and text == "/start" and (chat_id == sudo or chat_id == admin):
        bot('sendmessage', {
            'chat_id': chat_id,
            'text': f"*\n◉︙قسم الرشق \nيمنك اضافه او خصم رصيد\nيمكن قفل استقبال الرشق وفتحها\nيمكنك صنع هدايا \n*\n\nرصيدك في الموقع : *{flos}*\nالعمله : *{treqa}*\nاقل عدد لتحويل الرصيد : *{AKTHAR}*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(adm)
        })
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    if callback_query and data == "VIPME":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nيمكنك الاستمتاع بمميزات مدفوعه هنا\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnvip)
            })
            rshq.setdefault('mode', {})[from_id] = None
            SETJSON(rshq)
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\n◉︙هذا القسم للمشتركين المدفوعين فقط\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(admnb)
            })

    if callback_query and data == "setJa":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل كليشه الجوائز الان ياحبيبي\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "setJa":
        if chat_id == sudo or chat_id == admin:
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "*\nتم تعين الجوائز بنجاح \n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq['JAWA'] = text
            rshq.setdefault('mode', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and data == "offr":
        if chat_id == sudo or chat_id == admin:
            bot("deletemessage", {
                'chat_id': chat_id,
                'message_id': message_id,
            })
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "*\nتم القفل\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq['FREE'] = None
            SETJSON(rshq)

    if callback_query and data == "onfr":
        if chat_id == sudo or chat_id == admin:
            bot("deletemessage", {
                'chat_id': chat_id,
                'message_id': message_id,
            })
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "*\nتم الفتح \n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq['FREE'] = "TR"
            SETJSON(rshq)

    if callback_query and data == "xdmat":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\n◉︙قسم الخدمات في البوت ♥️\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{"text": "الاقسام", "callback_data": "qsmsa"}],
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and data == "qsmsa":
        key = {'inline_keyboard': []}
        for item in rshq.get('qsm', []):
            nameq, i = item.split("-", 1)
            if rshq.get('IFWORK>', {}).get(i) != "NOT":
                key['inline_keyboard'].append([{'text': nameq, 'callback_data': f"edits|{i}"}, {'text': "🗑", 'callback_data': f"delets|{i}"}])
        key['inline_keyboard'].append([{'text': "+ اضافه قسم جديد", "callback_data": "addqsm"}])
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "*\nالاقسام الموجوده في البوت\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    if callback_query and e[0] == "delets":
        rshq.setdefault('IFWORK>', {})[e[1]] = "NOT"
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

        key = {'inline_keyboard': []}
        for item in rshq.get('qsm', []):
            nameq, i = item.split("-", 1)
            if rshq.get('IFWORK>', {}).get(i) != "NOT":
                key['inline_keyboard'].append([{'text': nameq, 'callback_data': f"edits|{i}"}, {'text': "🗑", 'callback_data': f"delets|{i}"}])
        key['inline_keyboard'].append([{'text': "+ اضافه قسم جديد", "callback_data": "addqsm"}])
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "*\nالاقسام الموجوده في البوت\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })

    if callback_query and e[0] == "edits":
        key = {'inline_keyboard': []}
        bbERO = e[1]
        for hjjj, i in enumerate(rshq.get('xdmaxs', {}).get(bbERO, [])):
            key['inline_keyboard'].append([{'text': i, 'callback_data': f"editss|{bbERO}|{hjjj}"}, {'text': "🗑", 'callback_data': f"delt|{bbERO}|{hjjj}"}])
        key['inline_keyboard'].append([{'text': "+ اضافه خدمات الي هذا القسم", "callback_data": f"add|{bbERO}"}])
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nالخدمات الموجوده في قسم *{rshq.get('NAMES', {}).get(bbERO)}*\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = None
        rshq.setdefault('idTIMER', {})[random.randint(100, 900)] = rshq.get('NAMES', {}).get(bbERO)
        SETJSON(rshq)

    if callback_query and e[0] == "editss":
        dom = ""
        if rshq.get("sSite"):
            dom = f"ربط الخدمه علي الموقع الاساسي ({rshq['sSite']}) "

        key = {'inline_keyboard': []}
        key['inline_keyboard'].append([{'text': dom, 'callback_data': f"setauto|{e[1]}|{e[2]}"}])
        key['inline_keyboard'].append([{'text': "تعيين سعر الخدمه", "callback_data": f"setprice|{e[1]}|{e[2]}"}])
        key['inline_keyboard'].append([{'text': "تعيين ايدي الخدمه", "callback_data": f"setid|{e[1]}|{e[2]}"}])
        key['inline_keyboard'].append([{'text': "تعيين ادني حد للخدمه", "callback_data": f"setmin|{e[1]}|{e[2]}"}])
        key['inline_keyboard'].append([{'text': "تعيين اقصي حد للخدمه", "callback_data": f"setmix|{e[1]}|{e[2]}"}])
        key['inline_keyboard'].append([{'text': "تعيين وصف الخدمه", "callback_data": f"setdes|{e[1]}|{e[2]}"}])
        key['inline_keyboard'].append([{'text': "تعيين ربط الموقع", "callback_data": f"setWeb|{e[1]}|{e[2]}"}])
        key['inline_keyboard'].append([{'text': "تعيين API KEY الموقع للخدمه", "callback_data": f"setkey|{e[1]}|{e[2]}"}])
        key['inline_keyboard'].append([{'text': "امسح الخدمه", "callback_data": f"delt|{e[1]}|{e[2]}"}])
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nهنا خدمه {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2])]} في قسم {rshq.get('NAMES', {}).get(e[1])}\nيمكنك التحكم الكامل بلخدمات هنا ؟\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    if callback_query and e[0] == "delt":
        key = {'inline_keyboard': []}
        bbERO = e[1]
        xdmaxs_list = rshq.get('xdmaxs', {}).get(bbERO, [])
        if int(e[2]) < len(xdmaxs_list):
            del xdmaxs_list[int(e[2])]
        rshq.setdefault('xdmaxs', {})[bbERO] = xdmaxs_list

        for hjjj, i in enumerate(rshq.get('xdmaxs', {}).get(bbERO, [])):
            key['inline_keyboard'].append([{'text': i, 'callback_data': f"editss|{bbERO}|{hjjj}"}, {'text': "🗑", 'callback_data': f"delt|{bbERO}|{hjjj}"}])

        key['inline_keyboard'].append([{'text': "+ اضافه خدمات الي هذا القسم", "callback_data": f"add|{bbERO}"}])
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nالخدمات الموجوده في قسم *{rshq.get('NAMES', {}).get(bbERO)}*\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = None
        rshq.setdefault('idTIMER', {})[random.randint(100, 900)] = rshq.get('NAMES', {}).get(bbERO)
        SETJSON(rshq)

    if callback_query and e[0] == "setprice":
        key = {'inline_keyboard': []}
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nهنا خدمه {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2])]} في قسم {rshq.get('NAMES', {}).get(e[1])}\nارسل سعر الخدمه الان ؟\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = "setprice"
        rshq.setdefault('MGS', {})[from_id] = f"MGS|{e[1]}|{e[2]}"
        SETJSON(rshq)

    if callback_query and e[0] == "setauto":
        key = {'inline_keyboard': []}
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nهنا خدمه {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2])]} في قسم {rshq.get('NAMES', {}).get(e[1])}\nتم ربط الخدمه علي الموقع الاساسي 🔰\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = None
        rshq.setdefault('Web', {}).setdefault(e[1], {})[int(e[2])] = rshq.get("sSite")
        rshq.setdefault('key', {}).setdefault(e[1], {})[int(e[2])] = rshq.get("sToken")
        SETJSON(rshq)

    if callback_query and e[0] == "setmin":
        key = {'inline_keyboard': []}
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nهنا خدمه {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2])]} في قسم {rshq.get('NAMES', {}).get(e[1])}\nارسل ادني عدد للخدمه الان؟ \n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = "setmin"
        rshq.setdefault('MGS', {})[from_id] = f"MGS|{e[1]}|{e[2]}"
        SETJSON(rshq)

    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "setmin":
        if chat_id == sudo or chat_id == admin:
            mgs_parts = rshq.get('MGS', {}).get(from_id).split("|")
            qsm_id = mgs_parts[1]
            service_index = int(mgs_parts[2])
            bot("sendmessage", {
                "chat_id": chat_id,
                "text": f"تم تعيين ادني حد *{rshq.get('xdmaxs', {}).get(qsm_id, [])[service_index]}* في قسم *{rshq.get('NAMES', {}).get(qsm_id)}*",
                "parse_mode": "markdown",
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq.setdefault('min', {})
            rshq['min'].setdefault(qsm_id, {})[service_index] = int(text)
            rshq.setdefault('MGS', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and e[0] == "setkey":
        key = {'inline_keyboard': []}
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nهنا خدمه {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2])]} في قسم {rshq.get('NAMES', {}).get(e[1])}\nارسل API KEY الموقع الان؟ \n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = "setkey"
        rshq.setdefault('MGS', {})[from_id] = f"MGS|{e[1]}|{e[2]}"
        SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "setkey":
        if chat_id == sudo or chat_id == admin:
            mgs_parts = rshq.get('MGS', {}).get(from_id).split("|")
            qsm_id = mgs_parts[1]
            service_index = int(mgs_parts[2])
            bot("sendmessage", {
                "chat_id": chat_id,
                "text": f"تم تعيين API KEY *{rshq.get('xdmaxs', {}).get(qsm_id, [])[service_index]}* في قسم *{rshq.get('NAMES', {}).get(qsm_id)}*",
                "parse_mode": "markdown",
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq.setdefault('key', {})
            rshq['key'].setdefault(qsm_id, {})[service_index] = text
            rshq.setdefault('MGS', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and e[0] == "setmix":
        key = {'inline_keyboard': []}
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nهنا خدمه {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2])]} في قسم {rshq.get('NAMES', {}).get(e[1])}\nارسل اقصي حد للخدمه الان؟ \n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = "setmix"
        rshq.setdefault('MGS', {})[from_id] = f"MGS|{e[1]}|{e[2]}"
        SETJSON(rshq)

    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "setmix":
        if chat_id == sudo or chat_id == admin:
            mgs_parts = rshq.get('MGS', {}).get(from_id).split("|")
            qsm_id = mgs_parts[1]
            service_index = int(mgs_parts[2])
            bot("sendmessage", {
                "chat_id": chat_id,
                "text": f"تم تعيين اقصي حد *{rshq.get('xdmaxs', {}).get(qsm_id, [])[service_index]}* في قسم *{rshq.get('NAMES', {}).get(qsm_id)}*",
                "parse_mode": "markdown",
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq.setdefault('mix', {})
            rshq['mix'].setdefault(qsm_id, {})[service_index] = int(text)
            rshq.setdefault('MGS', {})[from_id] = None
            SETJSON(rshq)

    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "setprice":
        if chat_id == sudo or chat_id == admin:
            mgs_parts = rshq.get('MGS', {}).get(from_id).split("|")
            qsm_id = mgs_parts[1]
            service_index = int(mgs_parts[2])
            bot("sendmessage", {
                "chat_id": chat_id,
                "text": f"تم تعيين سعر *{rshq.get('xdmaxs', {}).get(qsm_id, [])[service_index]}* في قسم *{rshq.get('NAMES', {}).get(qsm_id)}*",
                "parse_mode": "markdown",
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq.setdefault('S3RS', {})
            rshq['S3RS'].setdefault(qsm_id, {})[service_index] = float(text) / 1000
            rshq.setdefault('MGS', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and e[0] == "setWeb":
        key = {'inline_keyboard': []}
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nهنا خدمه {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2])]} في قسم {rshq.get('NAMES', {}).get(e[1])}\nارسل رابط الموقع؟ \n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = "setWeb"
        rshq.setdefault('MGS', {})[from_id] = f"MGS|{e[1]}|{e[2]}"
        SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "setWeb":
        if chat_id == sudo or chat_id == admin:
            mgs_parts = rshq.get('MGS', {}).get(from_id).split("|")
            qsm_id = mgs_parts[1]
            service_index = int(mgs_parts[2])

            parsed_url = urlparse(text)
            inbero = parsed_url.netloc if parsed_url.netloc else text # Fallback to text if no netloc

            bot("sendmessage", {
                "chat_id": chat_id,
                "text": f"تم تعيين ربط موقع *{rshq.get('xdmaxs', {}).get(qsm_id, [])[service_index]}* في قسم *{rshq.get('NAMES', {}).get(qsm_id)}*",
                "parse_mode": "markdown",
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq.setdefault('Web', {})
            rshq['Web'].setdefault(qsm_id, {})[service_index] = inbero
            rshq.setdefault('MGS', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and e[0] == "setdes":
        key = {'inline_keyboard': []}
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nهنا خدمه {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2])]} في قسم {rshq.get('NAMES', {}).get(e[1])}\nارسل وصف الخدمه الان؟\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = "setdes"
        rshq.setdefault('MGS', {})[from_id] = f"MGS|{e[1]}|{e[2]}"
        SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "setdes":
        if chat_id == sudo or chat_id == admin:
            mgs_parts = rshq.get('MGS', {}).get(from_id).split("|")
            qsm_id = mgs_parts[1]
            service_index = int(mgs_parts[2])
            bot("sendmessage", {
                "chat_id": chat_id,
                "text": f"تم تعيين وصف ر *{rshq.get('xdmaxs', {}).get(qsm_id, [])[service_index]}* في قسم *{rshq.get('NAMES', {}).get(qsm_id)}*",
                "parse_mode": "markdown",
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq.setdefault('WSF', {})
            rshq['WSF'].setdefault(qsm_id, {})[service_index] = text
            rshq.setdefault('MGS', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and e[0] == "setid":
        key = {'inline_keyboard': []}
        key['inline_keyboard'].append([{'text': NamesBACK, "callback_data": "rshqG"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nهنا خدمه {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2])]} في قسم {rshq.get('NAMES', {}).get(e[1])}\nارسل ايدي الخدمه الان ؟\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = e[0]
        rshq.setdefault('MGS', {})[from_id] = f"MGS|{e[1]}|{e[2]}"
        SETJSON(rshq)

    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "setid":
        if chat_id == sudo or chat_id == admin:
            mgs_parts = rshq.get('MGS', {}).get(from_id).split("|")
            qsm_id = mgs_parts[1]
            service_index = int(mgs_parts[2])
            bot("sendmessage", {
                "chat_id": chat_id,
                "text": f"تم تعيين ايدي خدمه ر *{rshq.get('xdmaxs', {}).get(qsm_id, [])[service_index]}* في قسم *{rshq.get('NAMES', {}).get(qsm_id)}*",
                "parse_mode": "markdown",
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq.setdefault('IDSSS', {})
            rshq['IDSSS'].setdefault(qsm_id, {})[service_index] = int(text)
            rshq.setdefault('MGS', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and data == "addqsm":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل اسم القسم الان مثلا خدمات انستاكرام\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "xdmat"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "addqsm":
        if chat_id == sudo or chat_id == admin:
            b_e_r_o = "BERO" + str(random.randint(0, 999999999999999))
            bot("sendmessage", {
                "chat_id": chat_id,
                "text": f"تم اضافه هذا القسم بنجاح .\n- اسم القسم : {text}\n- كود القسم ( {b_e_r_o} )",
                "parse_mode": "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'للدخول لهذا القسم', 'callback_data': f"CHANGE|{b_e_r_o}"}],
                    ]
                })
            })
            rshq.setdefault('qsm', []).append(f"{text}-{b_e_r_o}")
            rshq.setdefault('NAMES', {})[b_e_r_o] = text
            rshq.setdefault('mode', {})[from_id] = None
            SETJSON(rshq)

    UUS = data.split("|") if callback_query else []
    if callback_query and UUS and UUS[0] == "CHANGE":
        if chat_id == sudo or chat_id == admin:
            bbERO = UUS[1]
            if rshq.get('NAMES', {}).get(bbERO) is not None:
                key = {'inline_keyboard': []}
                for hjjj, i in enumerate(rshq.get('xdmaxs', {}).get(bbERO, [])):
                    key['inline_keyboard'].append([{'text': i, 'callback_data': f"editss|{bbERO}|{hjjj}"}, {'text': "🗑", 'callback_data': f"delt|{bbERO}|{hjjj}"}])
                key['inline_keyboard'].append([{'text': "+ اضافه خدمه", "callback_data": f"add|{bbERO}"}])
                bot('EditMessageText', {
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'text': f"*\nمرحبا بك في هذا القسم {rshq.get('NAMES', {}).get(bbERO)}\n*",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps(key),
                })

    if callback_query and UUS and UUS[0] == "add":
        if chat_id == sudo or chat_id == admin:
            bbERO = UUS[1]
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': f"*\nارسل اسم الخدمه لاضافاتها الي قسم {bbERO}\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "xdmat"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = "adders"
            rshq.setdefault('idxs', {})[from_id] = UUS[1]
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "adders":
        if chat_id == sudo or chat_id == admin:
            bbERO = rshq.get('idxs', {}).get(from_id)
            # bsf = random.randint(33, 33333) # Not used, can be removed

            xdmaxs_list = rshq.setdefault('xdmaxs', {}).setdefault(bbERO, [])
            xdmaxs_list.append(text)
            hjjj = len(xdmaxs_list) - 1 # Index of the newly added service

            bot("sendmessage", {
                "chat_id": chat_id,
                "text": f"تم اضافه هذا الخدمه الي قسم *{rshq.get('NAMES', {}).get(bbERO)}*",
                "parse_mode": "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'دخول الي الخدمه', 'callback_data': f"editss|{bbERO}|{hjjj}"}],
                        [{'text': 'رجوع', 'callback_data': "xdmat"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq.setdefault('idxs', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and data == "onhdia":
        if chat_id == sudo or chat_id == admin:
            bot("deletemessage", {
                'chat_id': chat_id,
                'message_id': message_id,
            })
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "*\nتم تفعيل الهديه اليوميه .\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq['HDIA'] = "on"
            SETJSON(rshq)

    if callback_query and data == "ofhdia":
        if chat_id == sudo or chat_id == admin:
            bot("deletemessage", {
                'chat_id': chat_id,
                'message_id': message_id,
            })
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "*\nتم تعطيل الهديه اليوميه .\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq['HDIA'] = "of"
            SETJSON(rshq)

    if callback_query and data == "sAKTHAR":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل الان العدد ( ادني حد لتحويل رصيد (\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)

    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "sAKTHAR":
        bot("sendmessage", {
            'chat_id': chat_id,
            'text': f"تم التعيين بنجاح ادني حد للتحويل هو *{text}*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'رجوع', 'callback_data': "rshqG"}],
                ]
            })
        })
        rshq['AKTHAR'] = int(text)
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)
    elif message and text and not text.isnumeric() and rshq.get('mode', {}).get(from_id) == "sAKTHAR":
        bot("sendmessage", {
            'chat_id': chat_id,
            'text': "ارسل *الارقام* فقط عزيزي",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'رجوع', 'callback_data': "rshqG"}],
                ]
            })
        })

    if callback_query and data == "setphone":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل الان رقم الهاتف \n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)

    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "setphone":
        bot("sendmessage", {
            'chat_id': chat_id,
            'text': f"تم التعيين بنجاح رقم الهاتف هو *{text}*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'رجوع', 'callback_data': "rshqG"}],
                ]
            })
        })
        rshq['phone'] = text
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)
    elif message and text and not text.isnumeric() and rshq.get('mode', {}).get(from_id) == "setphone":
        bot("sendmessage", {
            'chat_id': chat_id,
            'text': "ارسل *الارقام* فقط عزيزي",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'رجوع', 'callback_data': "rshqG"}],
                ]
            })
        })

    if callback_query and data == "sethdia":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل الان عدد الهدیه الیومیه .\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = data
            SETJSON(rshq)

    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "sethdia":
        bot("sendmessage", {
            'chat_id': chat_id,
            'text': f"تم التعيين بنجاح عدد الهديه اليوميه هو *{text}*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'رجوع', 'callback_data': "rshqG"}],
                ]
            })
        })
        rshq['hdias'] = int(text)
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)
    elif message and text and not text.isnumeric() and rshq.get('mode', {}).get(from_id) == "sethdia":
        bot("sendmessage", {
            'chat_id': chat_id,
            'text': "ارسل *الارقام* فقط عزيزي",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'رجوع', 'callback_data': "rshqG"}],
                ]
            })
        })

    if callback_query and data == "infoRshq":
        if chat_id == sudo or chat_id == admin:
            sTok = rshq.get("sToken", "مامخلي توكن موقع انت")
            Sdom = rshq.get("sSite", "مامخلي دومين الموقع انت")
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': f"*\n◉︙معلومات الرشق\n*\n\nتوكن الموقع : `{sTok}`\nدومين موقع الرشق : `{Sdom}`\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and data == "token":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل الان توكن الموقع 🕸️\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = "sToken"
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "sToken":
        if chat_id == sudo or chat_id == admin:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"تم تعيين توكن الموقع\n- - - - - - - - - - - - - - - - - -\n`{text}`\n- - - - - - - - - - - - - - - - - - \n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq["sToken"] = text
            SETJSON(rshq)

    if callback_query and data == "SiteDomen":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل الان رابط الموقع مال الرشق 🧾\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = "SiteDomen"
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "SiteDomen":
        if chat_id == sudo or chat_id == admin:
            parsed_url = urlparse(text)
            inbero = parsed_url.netloc if parsed_url.netloc else text
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"تم تعيين موقع الرشق\n- - - - - - - - - - - - - - - - - -\n`{inbero}`\n- - - - - - - - - - - - - - - - - - \n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq["sSite"] = inbero
            SETJSON(rshq)

    if callback_query and data == "sCh":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل الان معرف القناة مع @ او بدون ⚜️\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = "sCh"
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "sCh":
        if chat_id == sudo or chat_id == admin:
            clean_text = text.replace("@", "")
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"تم تعيين قناة الاثباتات\n- - - - - - - - - - - - - - - - - -\n[@{clean_text}]\n- - - - - - - - - - - - - - - - - -\n- تأكد من ان البوت مشرف بالقناة {{⚠️}}\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = None
            rshq["sCh"] = f"@{clean_text}"
            SETJSON(rshq)

    if callback_query and data == "hdiamk":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل عدد الرصيد داخل الهديه \n\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = "hdiMk0"
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "hdiMk0":
        if chat_id == sudo or chat_id == admin:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': "جيد جدا صديقي .\nارسل الان عدد الاشخاص لاستخدام هذا الهديه وتحته اسم الاكود\nمثلا\n\n100\nBERO\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "admin"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = "hdiMk"
            rshq.setdefault('_HD', {})[from_id] = text
            # rshq[f"Bero{random.randint(999, 99999)}"] = f"on|{text}" # This line seems to create a random key not used elsewhere
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "hdiMk":
        if chat_id == sudo or chat_id == admin:
            lines = text.split("\n")
            if len(lines) >= 2:
                text1 = rshq.get('_HD', {}).get(from_id)
                mts = lines[1].strip()
                count_str = lines[0].strip()

                if count_str.isnumeric():
                    count = int(count_str)
                    bot('sendMessage', {
                        'chat_id': chat_id,
                        'text': f"تم اضافة كود هدية جديد\n- - - - - - - - - - - - - - - - - -\nالكود : `{mts}`\nعدد الرصيد : {text1}\nعدد الاشخاص : {count}\n- - - - - - - - - - - - - - - - - -\nبوت الرشق المجاني : [@{bot('getme')['result']['username']}] \n",
                        'parse_mode': "markdown",
                        'reply_markup': json.dumps({
                            'inline_keyboard': [
                                [{'text': NamesBACK, 'callback_data': "admin"}],
                            ]
                        })
                    })
                    rshq.setdefault('mode', {})[from_id] = None
                    rshq[mts] = f"on|{text1}|{count}"
                    rshq[f"A#D{mts}"] = str(count)
                    SETJSON(rshq)
                else:
                    bot('sendMessage', {
                        'chat_id': chat_id,
                        'text': "ارسل *الارقام* فقط!!",
                        'parse_mode': "markdown",
                        'reply_markup': json.dumps({
                            'inline_keyboard': [
                                [{'text': NamesBACK, 'callback_data': "admin"}],
                            ]
                        })
                    })
            else:
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': "الرجاء إرسال العدد واسم الكود في سطرين منفصلين.",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{'text': NamesBACK, 'callback_data': "admin"}],
                        ]
                    })
                })

    if callback_query and data == "onrshq":
        if chat_id == sudo or chat_id == admin:
            if rshq.get("sSite") is not None and rshq.get("sToken") is not None:
                bot('EditMessageText', {
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'text': "*\nتم فتح استقبال الرشق\n*",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{'text': NamesBACK, 'callback_data': "rshqG"}],
                        ]
                    })
                })
                rshq['rshqG'] = "on"
                SETJSON(rshq)
            else:
                bot('EditMessageText', {
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'text': "*\nلازم تكمل معلومات الرشق بلاول\n- التوكن او دومين موقع الرشق مامحطوط\n*",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{"text": "معلومات حول الرشق 📋", "callback_data": "infoRshq"}],
                            [{"text": "تعين توكن لموقع 🎟️", "callback_data": "token"}, {"text": "تعين موقع الرشق ⚙️", "callback_data": "SiteDomen"}],
                            [{'text': NamesBACK, 'callback_data': "rshqG"}],
                        ]
                    })
                })

    if callback_query and data == "ofrshq":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nتم قفل استقبال الرشق\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq['rshqG'] = "of"
            SETJSON(rshq)

    if callback_query and data == "coins":
        if chat_id == sudo or chat_id == admin:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nارسل ايدي الشخص الان\n\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "rshqG"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = "coins"
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "coins":
        if chat_id == sudo or chat_id == admin:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': "ارسل عدد الرصيد لاضافته للشخص\nاذا تريد تخصم كتب ويا -\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "admin"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = "coins2"
            rshq.setdefault('id', {})[from_id] = text
            SETJSON(rshq)

    if message and text and rshq.get('mode', {}).get(from_id) == "coins2":
        if chat_id == sudo or chat_id == admin:
            # Assuming 'text' here is the amount to add/subtract
            user_id_to_modify = rshq.get('id', {}).get(from_id)
            if user_id_to_modify:
                try:
                    amount = int(text)
                    rshq.setdefault('coin', {})[user_id_to_modify] = rshq.get('coin', {}).get(user_id_to_modify, 0) + amount
                    bot('sendMessage', {
                        'chat_id': chat_id,
                        'text': f"تم اضافه {amount} لـ {user_id_to_modify}",
                        'parse_mode': "markdown",
                        'reply_markup': json.dumps({
                            'inline_keyboard': [
                                [{'text': NamesBACK, 'callback_data': "admin"}],
                            ]
                        })
                    })
                    rshq.setdefault('mode', {})[from_id] = None
                    SETJSON(rshq)
                except ValueError:
                    bot('sendMessage', {
                        'chat_id': chat_id,
                        'text': "الرجاء إرسال رقم صحيح للرصيد.",
                        'parse_mode': "markdown",
                        'reply_markup': json.dumps({
                            'inline_keyboard': [
                                [{'text': NamesBACK, 'callback_data': "admin"}],
                            ]
                        })
                    })
            else:
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': "لم يتم تحديد ايدي المستخدم.",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{'text': NamesBACK, 'callback_data': "admin"}],
                        ]
                    })
                })


    coin = rshq.get("coin", {}).get(str(from_id), 0)
    bot_tlb = rshq.get('bot_tlb', 0)
    mytl = rshq.get("cointlb", {}).get(str(from_id), 0)
    share = rshq.get("mshark", {}).get(str(from_id), 0)
    coinss = rshq.get("coinss", {}).get(str(from_id), 0)
    tlby = rshq.get("tlby", {}).get(str(from_id), 0)

    RBEROO = {
        'inline_keyboard': [
            [{"text": "🚀┇قسم الرشق.", "callback_data": "service"}],
            [{"text": "🤑┇ربح رصيد .", "callback_data": "linkme"}, {"text": "✅┇شحن رصيدك .", "callback_data": "buy"}],
            [{"text": "🏷┇شحن كرت .", "callback_data": "hdia"}, {"text": "🔄┇تحويل رصيد .", "callback_data": "transer"}],
            [{"text": "☑️┇قناة البوت .", "url": f"https://t.me/{chabot}"}, {"text": "📦┇الحساب .", "callback_data": "acc"}],
            [{"text": "📨┇الدعم الفني .", "url": "https://t.me/Vl_HI"}]
        ]
    }

    if callback_query and data == "myrders":
        order_list_text = "\n".join(rshq.get("orders", {}).get(str(from_id), []))
        bot('editmessagetext', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"هذا هي طلباتك ✳️\n{order_list_text}\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "ارسال جميع الطلبات بصيغه الملف 📁", "callback_data": f"sendMeTxt|{from_id}"}],
                    [{"text": NamesBACK, "callback_data": "tobot"}],
                ]
            })
        })

    if callback_query and UUS and UUS[0] == "sendMeTxt":
        g_msg = bot('editmessagetext', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "يتم الترتيب 📤\n",
            'parse_mode': "markdown",
        })
        order_list_text = "\n".join(rshq.get("orders", {}).get(UUS[1], []))
        rb = random.randint(999, 99999)
        filename = f"oRD({rb})_{usrbot}.txt"
        write_file(filename, order_list_text)

        with open(filename, 'rb') as f_doc:
            bot("senddocument", {
                "chat_id": chat_id,
                "caption": "تم الارسال بنجاح (طلباتك)",
                "document": (filename, f_doc.read(), 'text/plain')
            })

        bot('editmessagetext', {
            'chat_id': chat_id,
            'message_id': g_msg['result']['message_id'],
            'text': f"هذا هي طلباتك ✳️\n{order_list_text}\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "ارسال جميع الطلبات بصيغه الملف 📁", "callback_data": f"sendMeTxt|{UUS[1]}"}],
                    [{"text": NamesBACK, "callback_data": "tobot"}],
                ]
            })
        })
        os.remove(filename)

    JAWA = rshq.get('JAWA')

    if callback_query and data == "termss":
        if rshq.get('KLISHA') is None:
            bot('editmessagetext', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': f"شروط استخدام بوت {nambot} \n\n- بوت {nambot} اول بوت عربي في التلجرام مخصص لجميع خدمات برامج التواصل الاجتماعي انستقرام - تيك توك - يوتيوب - تيوتر - فيسبوك وللخ... هناك العديد من الشروط حول استخدام بوت {nambot}.\n\n- الامان والثقه الموضوع الاول لدينا وحماية خصوصية جميع المستخدمين من الاولويات لدينا لذالك جميع المعلومات من الرصيد والطلبات هي محصنة تماماً لا يسمح لـ اي شخص الاطلاع عليها الا في حالة طلب المستخدم ذالك من الدعم الفني\n\n- على جميع المستخدمين التركيز في حالة طلب اي شيء من البوت في حالة كان حسابك او قناتك او ماشبه ذالك خاص سيلغي طلبك نهائياً لذالك لايوجد استرداد او اي تعويض لذالك وجب التنبيه\n\n- جميع الخدمات تتحدث يومياً لا يوجد لدينا خدمات ثابته يتم اضافة يومياً العديد من الخدمات التي تكون مناسبة لجميع المستخدمين في البوت لنكون الاول والافضل دائماً\n\n- لا يوجد اي استرداد او الغاء في حالة تم الرشق او الدعم لحساب او لقناة او لمنشور في الغلط \n\n- جميع الخدمات المتوفره هي موثوقه تماماً ويتم التجربه عليها قبل اضافاتها للبوت لذالك يتوفر انواع الخدمات بأسعار مختلفة من خدمة لخدمة اخرى\n\n- قنوات بوت {nambot} في التلجرام \nقناة بوت {nambot} @{chabot} القناة الرسميه التي يتم نشر بها جميع الخدمات والمعلومات حول بوت {nambot}\n\nقناة وكيل بوت {nambot} ( [@Vl_HI] - @Vl_HI ) القناة الرسميه لوكيل بوت {nambot} لذالك لا يتوفر لدينا سوا هذه القنوات المطروحه اعلاه واذا توفر لدينا اي قناة سنقوم بنشرها في قنواتنا الرسميه ليكون لدى جميع المستخدمين العلم بذالك\n\nفريق بوت {nambot} ✍\n",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })
        else:
            bot('editmessagetext', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': rshq['KLISHA'],
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })

    if callback_query and data == "JAWA":
        if rshq.get('JAWA') is None:
            bot('editmessagetext', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "لم يتم تعيين كليشه\n",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "linkme"}],
                    ]
                })
            })
        else:
            bot('editmessagetext', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': rshq['JAWA'],
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "linkme"}],
                    ]
                })
            })

    hHbero = rshq.get('HACKER', {}).get(from_id)
    if message and text == "/start" and hHbero == "I":
        e1_hack = rshq.get('HACK', {}).get(from_id)
        if e1_hack and str(e1_hack) != str(from_id):
            if str(from_id) not in rshq.get("3thu", []):
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': "لقد دخلت لرابط الدعوه الخاص بصديقك وحصل علي *5* رصيد\n",
                    'parse_mode': "markdown",
                })
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': f"*✅┇مرحبا بك في بوت  𓂀 الأڤـيـتـار 𓂀  *\n\n⚙┇رصيدك : *{coin}*\n📺┇ايديك : `{from_id}`\n🕹┇العملة : *نقاط*\n\n*⬇️┇تحكم بالازرار عبر الاسفل* \n",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps(RBEROO)
                })

                if str(e1_hack) not in BERO.get('BERO', {}).get('send', {}).get('uname', []):
                    BERO.setdefault('BERO', {}).setdefault('send', {}).setdefault('uname', []).append(str(e1_hack))
                    BERO.setdefault('BERO', {}).setdefault('send', {}).setdefault('add', []).append(1)
                else:
                    idx = BERO['BERO']['send']['uname'].index(str(e1_hack))
                    BERO['BERO']['send']['add'][idx] += 1

                write_file(f"RSHQ/BERO_{usrbot}.json", json.dumps(BERO, indent=4, ensure_ascii=False))

                rshq.setdefault('HACKER', {})[from_id] = None
                rshq.setdefault('HACK', {})[from_id] = None
                rshq.setdefault("3thu", []).append(str(from_id))
                rshq.setdefault("coin", {})[str(e1_hack)] = rshq.get("coin", {}).get(str(e1_hack), 0) + (rshq.get("coinshare") or 25)
                rshq.setdefault("mshark", {})[str(e1_hack)] = rshq.get("mshark", {}).get(str(e1_hack), 0) + 1
                SETJSON(rshq)
            else:
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': f"*✅┇مرحبا بك في بوت  𓂀 الأڤـيـتـار 𓂀  *\n\n⚙┇رصيدك : *{coin}*\n📺┇ايديك : `{from_id}`\n🕹┇العملة : *نقاط*\n\n*⬇️┇تحكم بالازرار عبر الاسفل* \n",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps(RBEROO)
                })
                rshq.setdefault('HACKER', {})[from_id] = None
                rshq.setdefault('HACK', {})[from_id] = None
                SETJSON(rshq)
        else:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': "لايمكنك الدخول لرابط الدعوه الخاص بك✅\n",
            })
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"*✅┇مرحبا بك في بوت  𓂀 الأڤـيـتـار 𓂀  *\n\n⚙┇رصيدك : *{coin}*\n📺┇ايديك : `{from_id}`\n🕹┇العملة : *نقاط*\n\n*⬇️┇تحكم بالازرار عبر الاسفل* \n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(RBEROO)
            })
            rshq.setdefault('HACKER', {})[from_id] = None
            rshq.setdefault('HACK', {})[from_id] = None
            SETJSON(rshq)
    elif message and text == "/start": # General /start
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"*✅┇مرحبا بك في بوت  𓂀 الأڤـيـتـار 𓂀  *\n\n⚙┇رصيدك : *{coin}*\n📺┇ايديك : `{from_id}`\n🕹┇العملة : *نقاط*\n\n*⬇️┇تحكم بالازرار عبر الاسفل* \n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(RBEROO)
        })

    if message and text == "MMTEST":
        # b is not defined in this scope. Assuming it's meant to be some dynamic text
        # For now, just a placeholder.
        b = "Test message content"
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"{b}\n",
            'parse_mode': "markdown",
        })

    e_parts = text.split(" ") if message and text else []
    if message and len(e_parts) == 2 and e_parts[0] == "/start" and e_parts[1].isnumeric() and not re.search("#Bero#", text):
        e1_num = e_parts[1]
        if str(e1_num) != str(from_id):
            if str(from_id) not in rshq.get("3thu", []):
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': "لقد دخلت لرابط الدعوه الخاص بصديقك وحصل علي *5* رصيد\n",
                    'parse_mode': "markdown",
                })
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': f"*✅┇مرحبا بك في بوت  𓂀 الأڤـيـتـار 𓂀  *\n\n⚙┇رصيدك : *{coin}*\n📺┇ايديك : `{from_id}`\n🕹┇العملة : *نقاط*\n\n*⬇️┇تحكم بالازرار عبر الاسفل* \n",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps(RBEROO)
                })

                if str(e1_num) not in BERO.get('BERO', {}).get('send', {}).get('uname', []):
                    BERO.setdefault('BERO', {}).setdefault('send', {}).setdefault('uname', []).append(str(e1_num))
                    BERO.setdefault('BERO', {}).setdefault('send', {}).setdefault('add', []).append(1)
                else:
                    idx = BERO['BERO']['send']['uname'].index(str(e1_num))
                    BERO['BERO']['send']['add'][idx] += 1
                write_file(f"RSHQ/BERO_{usrbot}.json", json.dumps(BERO, indent=4, ensure_ascii=False))

                rshq.setdefault("3thu", []).append(str(from_id))
                rshq.setdefault("coin", {})[str(e1_num)] = rshq.get("coin", {}).get(str(e1_num), 0) + (rshq.get("coinshare") or 25)
                rshq.setdefault("mshark", {})[str(e1_num)] = rshq.get("mshark", {}).get(str(e1_num), 0) + 1
                SETJSON(rshq)
            else:
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': f"*✅┇مرحبا بك في بوت  𓂀 الأڤـيـتـار 𓂀  *\n\n⚙┇رصيدك : *{coin}*\n📺┇ايديك : `{from_id}`\n🕹┇العملة : *نقاط*\n\n*⬇️┇تحكم بالازرار عبر الاسفل* \n",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps(RBEROO)
                })
        else:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': "لايمكنك الدخول لرابط الدعوه الخاص بك✅\n",
            })
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"*✅┇مرحبا بك في بوت  𓂀 الأڤـيـتـار 𓂀  *\n\n⚙┇رصيدك : *{coin}*\n📺┇ايديك : `{from_id}`\n🕹┇العملة : *نقاط*\n\n*⬇️┇تحكم بالازرار عبر الاسفل* \n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(RBEROO)
            })
    elif message and text == "/start": # General /start
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"*✅┇مرحبا بك في بوت  𓂀 الأڤـيـتـار 𓂀  *\n\n⚙┇رصيدك : *{coin}*\n📺┇ايديك : `{from_id}`\n🕹┇العملة : *نقاط*\n\n*⬇️┇تحكم بالازرار عبر الاسفل* \n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(RBEROO)
        })

    if callback_query and data == "buy":
        if rshq.get('buy') is None:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*☑️┇يمكن شحن رصيدك في Ξ بوت  𓂀 الأڤـيـتـار 𓂀   بطرق دفع عديدة. 👇\n\n✳️ PAYEER, Perfect Money, BTC ,LTC\n✳️ Kuraimi, SabaFon ,STC ,others..\n\n✳️┇نقبل جميع طرق الدفع من اليمن،السعودية،العراق،مصر وطرق دفع عالمية اخرى.\n\n👨‍✈️┇الإدراة : @Vl_HI*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': rshq['buy'],
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })

    if callback_query and data == "tobot":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*✅┇مرحبا بك في بوت  𓂀 الأڤـيـتـار 𓂀  *\n\n⚙┇رصيدك : *{coin}*\n📺┇ايديك : `{from_id}`\n🕹┇العملة : *نقاط*\n\n*⬇️┇تحكم بالازرار عبر الاسفل* \n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(RBEROO)
        })

    if callback_query and data == "hdia":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "💳 ارسل الكود :\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                ]
            })
        })
        rshq.setdefault('mode', {})[from_id] = "hdia"
        SETJSON(rshq)

    if callback_query and data == "transer":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "ارسل عدد الرصيد لتحويله 🎉\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                ]
            })
        })
        rshq.setdefault('mode', {})[from_id] = data
        SETJSON(rshq)

    MakLink = ''.join(random.sample('AbCdEfGhIjKlMnOpQrStU12345689807', 13))
    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "transer":
        if rshq.get("coin", {}).get(str(from_id), 0) >= int(text):
            if not re.search(r'\+|-', text): # Check for + or - to prevent "cheating"
                if int(text) >= AKTHAR:
                    bot('sendMessage', {
                        'chat_id': chat_id,
                        'text': f"تم صنع رابط تحويل بقيمه {text} رصيد 💲\n- وتم استقطاع *{text}* من رصيدك ➖\n\nالرابط : https://t.me/{bot('getme')['result']['username']}?start=Bero{MakLink}\n\nايدي وصل التحويل : `{base64.b64encode(MakLink.encode()).decode()}`\n\nصار عدد رصيدك : *{rshq.get('coin', {}).get(str(from_id), 0) - int(text)}*\n",
                        'parse_mode': "markdown",
                        'reply_markup': json.dumps({
                            'inline_keyboard': [
                                [{'text': NamesBACK, 'callback_data': "tobot"}],
                            ]
                        })
                    })
                    rshq.setdefault("coin", {})[str(from_id)] -= int(text)
                    rshq.setdefault('mode', {})[from_id] = None
                    rshq.setdefault('thoiler', {})[MakLink] = {"coin": int(text), "to": from_id}
                    SETJSON(rshq)
                else:
                    bot('sendMessage', {
                        'chat_id': chat_id,
                        'text': f"يمكنك تحويل رصيد اكثر من {AKTHAR} فقط\n",
                        'parse_mode': "markdown",
                        'reply_markup': json.dumps({
                            'inline_keyboard': [
                                [{'text': NamesBACK, 'callback_data': "tobot"}],
                            ]
                        })
                    })
            else:
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': "لاتحاول استخدام الكلجاا�� سيتم حظرك عام؟ 👎\n",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{'text': NamesBACK, 'callback_data': "tobot"}],
                        ]
                    })
                })
        else:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': "رصيدك غير كافيه ❌🗣️\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })

    if message and text and rshq.get('mode', {}).get(from_id) == "hdia":
        code_info = rshq.get(text)
        if code_info:
            code_parts = code_info.split("|")
            if code_parts[0] == "on":
                # Ensure 'mehdia' is initialized as a dict for the user if it doesn't exist
                if not isinstance(rshq.get('mehdia', {}).get(str(from_id)), dict):
                    rshq.setdefault('mehdia', {})[str(from_id)] = {}

                if text not in rshq.get('mehdia', {}).get(str(from_id), {}):
                    # Corrected condition for using the code
                    if int(code_parts[2]) > rshq.get(f"TASY_{text}", 0):
                        bot('sendMessage', {
                            'chat_id': chat_id,
                            'text': f"تم اضافة {code_parts[1]}$ الى حسابك ✅\n",
                            'parse_mode': "markdown",
                            'reply_markup': json.dumps({
                                'inline_keyboard': [
                                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                                ]
                            })
                        })
                        bot('sendMessage', {
                            'chat_id': admin,
                            'text': f"هذا اخذ كود الهديه بقيمه{code_parts[1]}\n\n~ [{name}](tg://user?id={chat_id}) \n",
                            'parse_mode': "markdown",
                            'reply_markup': json.dumps({
                                'inline_keyboard': [
                                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                                ]
                            })
                        })
                        rshq[f"TASY_{text}"] = rshq.get(f"TASY_{text}", 0) + 1
                        rshq.setdefault('mode', {})[from_id] = None
                        rshq.setdefault('mehdia', {})[str(from_id)][text] = "on"
                        rshq.setdefault("coin", {})[str(from_id)] = rshq.get("coin", {}).get(str(from_id), 0) + int(code_parts[1])
                        SETJSON(rshq)
                    else:
                        bot('sendMessage', {
                            'chat_id': chat_id,
                            'text': "الكود خطأ او تم استخدامه ❌\n",
                            'parse_mode': "markdown",
                            'reply_markup': json.dumps({
                                'inline_keyboard': [
                                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                                ]
                            })
                        })
                        rshq.setdefault('mode', {})[from_id] = None
                        SETJSON(rshq)
                else:
                    bot('sendMessage', {
                        'chat_id': chat_id,
                        'text': "الكود خطأ او تم استخدامه ❌\n",
                        'parse_mode': "markdown",
                        'reply_markup': json.dumps({
                            'inline_keyboard': [
                                [{'text': NamesBACK, 'callback_data': "tobot"}],
                            ]
                        })
                    })
            else:
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': "الكود خطأ او تم استخدامه ❌\n",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{'text': NamesBACK, 'callback_data': "tobot"}],
                        ]
                    })
                })
                rshq.setdefault('mode', {})[from_id] = None
                SETJSON(rshq)
        else:
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': "الكود خطأ او تم استخدامه ❌\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })
            rshq.setdefault('mode', {})[from_id] = None
            SETJSON(rshq)

    if callback_query and data == "plus":
        if HDIAS:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "✳️ تجميع رصيد\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{"text": "رابط الدعوه 🌀", "callback_data": "linkme"}],
                        [{"text": HDIAS, "callback_data": "hdiaa"}],
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "✳️ تجميع رصيد\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{"text": "رابط الدعوه 🌀", "callback_data": "linkme"}],
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })

    # Assuming BERO.json contains a structure like:
    # {"BERO": {"send": {"uname": ["user_id1", "user_id2"], "add": [count1, count2]}}}
    BERO_content = {}
    try:
        with open(f"RSHQ/BERO_{usrbot}.json", 'r', encoding='utf-8') as f:
            BERO_content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        BERO_content = {"BERO": {"send": {"uname": [], "add": []}}}

    f_values = BERO_content.get('BERO', {}).get('send', {}).get('add', [])
    u_names = BERO_content.get('BERO', {}).get('send', {}).get('uname', [])

    # Create a list of (value, uname) tuples for sorting
    combined_data = sorted([(f_values[i], u_names[i]) for i in range(len(f_values))], key=lambda x: x[0], reverse=True)

    ok = ""
    # Numbers = ['1', '2', '3', '4', '5'] # Not used
    NumbersBe = ['🏆', '🥈', '🥉', '4️⃣', '5️⃣']

    for i in range(min(5, len(combined_data))):
        count, uS = combined_data[i]

        # Get chat info to display title or username
        chat_info = bot("getChat", {'chat_id': uS})
        fk = uS
        if chat_info and chat_info.get('ok') and chat_info['result'].get('title'):
            fk = chat_info['result']['title']
        elif chat_info and chat_info.get('ok') and chat_info['result'].get('username'):
            fk = f"@{chat_info['result']['username']}"

        u_display = NumbersBe[i] # Use the corresponding emoji
        ok += f"{u_display} ) ❲*{count}*❳ -> [{fk}](tg://user?id={uS})\n"

    b_leaderboard = f"🌀] الاعلى في الدعوات : \n{ok}"

    if callback_query and data == "linkme":
        # sx = rshq.get("coinshare") or "1" # sx not used
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*☑️┇يمكنك الآن الحصول على رصيد مجاني من خلال مشاركة رابط الدعوة الخاص بك 💰➕.\n\n🔗︙الرابط الخاص بك : https://t.me/{usrbot_info['result']['username']}?start={from_id}\n\n📘︙شارك رابط الدعوة الخاص بك مع أصدقائك او قنواتك او اي مكان ، واحصل على 1 رصيد مجاناً لكل شخص يقوم بالدخول عبر رابطك ☑️.*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                ]
            })
        })

    today_file = f"{d}_{usrbot}.txt"
    day_users = []
    try:
        with open(today_file, 'r', encoding='utf-8') as f:
            day_users = f.read().splitlines()
    except FileNotFoundError:
        pass

    # Unlink old files
    if d == "Sat" and os.path.exists(f"Fri_{usrbot}.txt"): os.remove(f"Fri_{usrbot}.txt")
    if d == "Sun" and os.path.exists(f"Sat_{usrbot}.txt"): os.remove(f"Sat_{usrbot}.txt")
    if d == "Mon" and os.path.exists(f"Sun_{usrbot}.txt"): os.remove(f"Sun_{usrbot}.txt")
    if d == "Tue" and os.path.exists(f"Mon_{usrbot}.txt"): os.remove(f"Mon_{usrbot}.txt")
    if d == "Wed" and os.path.exists(f"Tue_{usrbot}.txt"): os.remove(f"Tue_{usrbot}.txt")
    if d == "Thu" and os.path.exists(f"Wed_{usrbot}.txt"): os.remove(f"Wed_{usrbot}.txt")
    if d == "Fri" and os.path.exists(f"Thu_{usrbot}.txt"): os.remove(f"Thu_{usrbot}.txt")

    if callback_query and data == "hdiaa":
        if str(from_id) not in day_users:
            HDIASs = rshq.get('hdias', 20)
            bot('answercallbackquery', {
                'callback_query_id': update['callback_query']['id'],
                'text': f"✳️] لقد حصلت علي {HDIASs}$",
                'show_alert': True,
            })
            rshq.setdefault("coin", {})[str(from_id)] = rshq.get("coin", {}).get(str(from_id), 0) + HDIASs

            with open(today_file, 'a', encoding='utf-8') as f:
                f.write(f"{from_id}\n")

            # Recalculate 'coin' for the display after update
            current_coin = rshq.get("coin", {}).get(str(from_id), 0)

            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': f"*✅┇اهلا وسهلا بك :\n\n☑️┇ رصيدك: {current_coin}\n🔥┇الرصيد المستهلك : {(rshq.get('cointlb', {}).get(str(from_id), 0))}\n🌻┇عدد ارباح الدعوة عبر رابطك : {share}\n🤖┇عدد طلباتك : {tlby}\n\n🌺┇للرجوع اضغط الزر ادناه*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })
            SETJSON(rshq)
        else:
            time_until_tomorrow = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time.min) - datetime.datetime.now()
            hours_left = int(time_until_tomorrow.total_seconds() // 3600)

            bot('answercallbackquery', {
                'callback_query_id': update['callback_query']['id'],
                'text': f"طالب بالهدية اليوميه بعد {hours_left} ساعه",
                'show_alert': True,
            })

    if callback_query and data == "info":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "*\nالبوت الاول في التليجرام لزيادة متابعين الانستقرام بشكل فوري و سريع و بنسبة ثبات 99% \n\n    كل ماعليك هو دعوة اصدقائك من خلال الرابط الخاص بك وستحصل على متابعين مقابل كل شخص تحصل تدعوه تحصل على 10 رصيد\n    \n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                ]
            })
        })

    if callback_query and data == "mstqbll":
        if rshq.get('rshqG') == "on":
            ster = "مفتوح ✅"
            wsfer = "يمكنك الرشق ✅"
        else:
            ster = "مقفل ❌"
            wsfer = "لايمكنك الرشق حاليا اجمع رصيد لحد ما ينفتح ❌"
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*\nاستقبال الرشق {ster}\n- {wsfer}\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                ]
            })
        })

    e1_start_bero = text.replace("/start Bero", "") if message and text and text.startswith("/start Bero") else None
    if e1_start_bero:
        if rshq.get('thoiler', {}).get(e1_start_bero, {}).get("to") is not None:
            thoiler_info = rshq['thoiler'][e1_start_bero]
            bot('sendMessage', {
                'chat_id': chat_id,
                'text': f"لقد حصلت علي *{thoiler_info['coin']}* رصيد من رابط التحويل\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })
            bot('sendMessage', {
                'chat_id': thoiler_info['to'],
                'text': f"تحويل مكتمل 💯\n\nمعلومات الي دخل للرابط ✅\nاسمه : [{name}](tg://user?id={chat_id})\nايديه : `{from_id}`\n\nوتم تحويل{thoiler_info['coin']} رصيد لحسابه\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })
            del rshq['thoiler'][e1_start_bero] # Remove used link
            rshq.setdefault("coin", {})[str(from_id)] = rshq.get("coin", {}).get(str(from_id), 0) + thoiler_info['coin']
            SETJSON(rshq)
        else:
            bot('sendMessage', {
                'chat_id': from_id,
                'text': "رابط التحويل هذا غير صالح ❌\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': NamesBACK, 'callback_data': "tobot"}],
                    ]
                })
            })

    if callback_query and data == "acc":
        time_until_tomorrow = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time.min) - datetime.datetime.now()
        hours_left = int(time_until_tomorrow.total_seconds() // 3600)

        # Check if already claimed today
        if str(from_id) not in day_users:
            daily_gift_status = "تستطيع المطالبة بها 🎁"
        else:
            daily_gift_status = f"متبقي {hours_left} ساعة على الهدية اليومية"

        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"*✅┇اهلا وسهلا بك :\n\n☑️┇ رصيدك: {coin}\n🔥┇الرصيد المستهلك : {(rshq.get('cointlb', {}).get(str(from_id), 0))}\n🌻┇عدد ارباح الدعوة عبر رابطك : {share}\n🤖┇عدد طلباتك : {tlby}\n🎁┇الهدية اليومية : {daily_gift_status}\n\n🌺┇للرجوع اضغط الزر ادناه*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                ]
            })
        })

    if callback_query and data == "service":
        if rshq.get('rshqG') == "on":
            key = {'inline_keyboard': []}
            for item in rshq.get('qsm', []):
                nameq, i = item.split("-", 1)
                if rshq.get('IFWORK>', {}).get(i) != "NOT":
                    key['inline_keyboard'].append([{'text': nameq, 'callback_data': f"BEROENT|{i}"}])
            key['inline_keyboard'].append([{'text': NamesBACK, 'callback_data': "tobot"}])
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': f"👥] نقاطك : {coin}\n🔢] ايديك : {from_id}\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps(key),
            })
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "*\nتم قفل استقبال الرشق عزيزي\nاجمع رصيد الان علماينفتح الرشق\n*",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع', 'callback_data': "tobot"}],
                    ]
                })
            })

    if callback_query and UUS and UUS[0] == "BEROENT":
        key = {'inline_keyboard': []}
        bbERO = UUS[1]
        for hjjj, i in enumerate(rshq.get('xdmaxs', {}).get(bbERO, [])):
            key['inline_keyboard'].append([{'text': i, 'callback_data': f"type|{bbERO}|{hjjj}"}])
        key['inline_keyboard'].append([{'text': NamesBACK, 'callback_data': "service"}])
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "✳️] اختر الخدمات التي تريدها :\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(key),
        })
        rshq.setdefault('mode', {})[from_id] = None
        SETJSON(rshq)

    if callback_query and data == "infotlb":
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': "*\n🔢] ارسل ايدي الطلب :\n*",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'رجوع', 'callback_data': "tobot"}],
                ]
            })
        })
        rshq.setdefault('mode', {})[from_id] = data
        SETJSON(rshq)

    current_site = rshq.get("sSite")
    current_api_token = rshq.get("sToken")

    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "infotlb":
        order_id = text
        site_for_order = rshq.get("sites", {}).get(order_id, current_site)
        key_for_order = rshq.get("keys", {}).get(order_id, current_api_token)

        if site_for_order and key_for_order:
            req_response = None
            try:
                req_response = requests.get(f"https://{site_for_order}/api/v2?key={key_for_order}&action=status&order={order_id}")
                req_response.raise_for_status()
                req = req_response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching order status: {e}")
                req = {}

            # startcc = req.get('start_count') # Not used
            remains = req.get('remains')
            status_text = ""
            if remains is not None and remains == 0:
                status_text = "طلب مكتمل 🟢"
            else:
                status_text = "قيد المراجعة"

            if req_response and req_response.ok: # Check if the request was successful
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': f"️⃣] معلومات عن الطلب :\n\n- 🔡] اسم الخدمة : {rshq.get('ordn', {}).get(order_id, 'غير معروف')}\n- 🔢] ايدي الطلب : `{order_id}`\n- ♻️] حالة الطلب : {status_text}\n- ⏳] المتبقي : {remains}\n",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{"text": "تحديث", "callback_data": f"updates|{order_id}"}],
                            [{"text": "رجوع", "callback_data": "tobot"}],
                        ]
                    })
                })
                rshq.setdefault('mode', {})[from_id] = None
                SETJSON(rshq)
            else:
                bot('sendMessage', {
                    'chat_id': chat_id,
                    'text': "️هذا الطلب ليس موجود في طلباتك ❌\n",
                    'parse_mode': "markdown",
                })
        else:
             bot('sendMessage', {
                'chat_id': chat_id,
                'text': "️لا تتوفر معلومات الموقع أو مفتاح API لهذا الطلب ❌\n",
                'parse_mode': "markdown",
            })

    if callback_query and e and e[0] == "updates":
        order_id = e[1]
        site_for_order = rshq.get("sites", {}).get(order_id, current_site)
        key_for_order = rshq.get("keys", {}).get(order_id, current_api_token)

        if site_for_order and key_for_order:
            req_response = None
            try:
                req_response = requests.get(f"https://{site_for_order}/api/v2?key={key_for_order}&action=status&order={order_id}")
                req_response.raise_for_status()
                req = req_response.json()
            except requests.exceptions.RequestException as ex:
                print(f"Error fetching order status for update: {ex}")
                req = {}

            # startcc = req.get('start_count') # Not used
            remains = req.get('remains')
            sberero = ""
            if remains is not None and remains == 0:
                sberero = "طلب مكتمل 🟢"
            else:
                sberero = "قيد الانتضار ...."

            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': f"️⃣] معلومات عن الطلب :\n\n- 🔡] اسم الخدمة : {rshq.get('ordn', {}).get(order_id, 'غير معروف')}\n- 🔢] ايدي الطلب : `{order_id}`\n- ♻️] حالة الطلب : {sberero}\n- ⏳] المتبقي : {remains}\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{"text": "تحديث", "callback_data": f"updates|{order_id}"}],
                        [{"text": "رجوع", "callback_data": "tobot"}],
                    ]
                })
            })
        else:
            bot('EditMessageText', {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': "️لا تتوفر معلومات الموقع أو مفتاح API لهذا الطلب ❌\n",
                'parse_mode': "markdown",
            })

    if callback_query and e and e[0] == "type":
        service_id_in_list = int(e[2])
        service_qsm_id = e[1]

        # Default values if not set in rshq
        s3r = rshq.get('S3RS', {}).get(service_qsm_id, {}).get(service_id_in_list)
        web = rshq.get('Web', {}).get(service_qsm_id, {}).get(service_id_in_list) or rshq.get("sSite")
        s3r = s3r if s3r is not None else 1.0 # Default to 1.0 if not set
        key_val = rshq.get('key', {}).get(service_qsm_id, {}).get(service_id_in_list) or rshq.get("sToken")
        mix_val = rshq.get('mix', {}).get(service_qsm_id, {}).get(service_id_in_list) or 1000
        min_val = rshq.get('min', {}).get(service_qsm_id, {}).get(service_id_in_list) or 100

        g = s3r * 1000

        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"👮🏽] اسم الخدمة : {rshq.get('xdmaxs', {}).get(service_qsm_id, [])[service_id_in_list]}\n\n💰] السعر : {g} $ لكل 1000\n\n📊] الحد الادني للرشق : {min_val}\n🎟️] الحد الاقصي للرشق : {mix_val}\n\n🦾] ارسل الكمية التي تريد طلبها :\n\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'رجوع', 'callback_data': "tobot"}],
                ]
            })
        })

        rshq.setdefault('IDX', {})[from_id] = rshq.get('IDSSS', {}).get(service_qsm_id, {}).get(service_id_in_list)
        rshq.setdefault('WSFV', {})[from_id] = rshq.get('WSF', {}).get(service_qsm_id, {}).get(service_id_in_list)
        rshq.setdefault('S3RS', {})[from_id] = s3r
        rshq.setdefault('web', {})[from_id] = web
        rshq.setdefault('key', {})[from_id] = key_val
        rshq.setdefault('min_mix', {})[from_id] = f"{min_val}|{mix_val}"
        rshq.setdefault('SB1', {})[from_id] = service_qsm_id
        rshq.setdefault('mode', {})[from_id] = "SETd"
        rshq.setdefault('SB2', {})[from_id] = service_id_in_list
        rshq.setdefault('=', {})[from_id] = rshq.get('xdmaxs', {}).get(service_qsm_id, [])[service_id_in_list]
        SETJSON(rshq)

    if callback_query and e and e[0] == "kmiat":
        s3r_for_kmiat = rshq.get('S3RS', {}).get(from_id)
        s3r_for_kmiat = s3r_for_kmiat if s3r_for_kmiat is not None else 1.0
        g_kmiat = s3r_for_kmiat * 1000

        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"👮🏽] اسم الخدمة : {rshq.get('xdmaxs', {}).get(e[1], [])[int(e[2]) if len(e) > 2 else 0]}\n\n💰] السعر : {g_kmiat} $ لكل 1000\n\n🦾] اختر الكمية التي تريد طلبها :\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': 'السعر', 'callback_data': f"type|{e[1]}|{e[2] if len(e) > 2 else ''}"}, {'text': 'العدد', 'callback_data': f"type|{e[1]}|{e[2] if len(e) > 2 else ''}"}],
                    [{'text': f"$ {s3r_for_kmiat * 1000}", 'callback_data': f"to|1000|{e[1]}"}, {'text': '1000 $', 'callback_data': f"to|1000|{e[1]}"}],
                    [{'text': f"$ {s3r_for_kmiat * 2000}", 'callback_data': f"to|2000|{e[1]}"}, {'text': '2000 $', 'callback_data': f"to|2000|{e[1]}"}],
                    [{'text': f"$ {s3r_for_kmiat * 4000}", 'callback_data': f"to|4000|{e[1]}"}, {'text': '4000 $', 'callback_data': f"to|4000|{e[1]}"}],
                    [{'text': f"$ {s3r_for_kmiat * 8000}", 'callback_data': f"to|8000|{e[1]}"}, {'text': '8000 $', 'callback_data': f"to|8000|{e[1]}"}],
                    [{'text': f"$ {s3r_for_kmiat * 10000}", 'callback_data': f"to|10000|{e[1]}"}, {'text': '10000 $', 'callback_data': f"to|10000|{e[1]}"}],
                    [{'text': f"$ {s3r_for_kmiat * 20000}", 'callback_data': f"to|20000|{e[1]}"}, {'text': '20000 $', 'callback_data': f"to|400|{e[1]}"}],
                    [{'text': 'رجوع', 'callback_data': f"type|{rshq.get('SB1', {}).get(from_id)}|{rshq.get('SB2', {}).get(from_id)}"}],
                ]
            })
        })

    if callback_query and data == "tobon":
        bot("deletemessage", {"message_id": message_id, "chat_id": chat_id})
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': "تم الالغاء بنجاح |\n",
            'parse_mode': "markdown",
        })
        bot('sendMessage', {
            'chat_id': chat_id,
            'text': f"مرحبا بك في بوت {nambot} 👋\n👥] رصيدك : *{coin}*\n🔢] ايديك : `{from_id}`\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps(RBEROO)
        })
        # Reset relevant rshq state variables
        if from_id in rshq.get('3dd', {}):
            rshq['3dd'][from_id][from_id] = None
        rshq.setdefault('mode', {})[from_id] = None
        rshq.setdefault("tlbia", {})[from_id] = None
        rshq.setdefault("cointlb", {})[from_id] = None
        rshq.setdefault("s3rltlb", {})[from_id] = None
        rshq.setdefault('tp', {})[from_id] = None
        rshq['coinn'] = None
        SETJSON(rshq)


    if message and text and text.isnumeric() and rshq.get('mode', {}).get(from_id) == "SETd":
        quantity = int(text)
        s3r_current = rshq.get('S3RS', {}).get(from_id)
        s3r_current = s3r_current if s3r_current is not None else 1.0

        cost = s3r_current * quantity
        min_val, mix_val = map(int, rshq.get('min_mix', {}).get(from_id, "100|1000").split("|"))

        if coin >= cost:
            if rshq.get('rshqG') == "on":
                if quantity >= min_val:
                    if quantity <= mix_val:
                        bot('sendmessage', {
                            'chat_id': chat_id,
                            'text': f"{rshq.get('WSFV', {}).get(from_id)}\n• ارسل الرابط الخاص بك 📥 :\n",
                            'reply_markup': json.dumps({
                                'inline_keyboard': [
                                    [{'text': 'رجوع + الغاء', 'callback_data': "tobon"}],
                                ]
                            })
                        })
                        rshq.setdefault('3dd', {}).setdefault(from_id, {})[from_id] = quantity
                        rshq.setdefault('mode', {})[from_id] = "MJK"
                        rshq.setdefault("s3rltlb", {})[from_id] = cost
                        # rshq.setdefault('tp', {})[from_id] = e[2] # e[2] is not defined here. This needs to come from previous step if used.
                        rshq['coinn'] = cost
                        SETJSON(rshq)
                    else:
                        bot('sendmessage', {
                            'chat_id': chat_id,
                            'text': f"*\n• العدد كبير جدا\n• ارسل عدد اصغر او يساوي {mix_val} 😅\n*",
                            'parse_mode': "markdown",
                            'reply_markup': json.dumps({
                                'inline_keyboard': [
                                    [{'text': 'رجوع + الغاء', 'callback_data': "tobon"}],
                                ]
                            })
                        })
                else:
                    bot('sendmessage', {
                        'chat_id': chat_id,
                        'text': f"*\n• العدد صغير جدا 🤏\n• ارسل عدد اكبر من او يساوي {min_val} 🎟️\n*",
                        'parse_mode': "markdown",
                        'reply_markup': json.dumps({
                            'inline_keyboard': [
                                [{'text': 'رجوع + الغاء', 'callback_data': "tobon"}],
                                ]
                            })
                        })
            else:
                bot('sendmessage', {
                    'chat_id': chat_id,
                    'text': "*\nتم قفل استقبال الرشق عزيزي\nاجمع رصيد الان علماينفتح الرشق\n*",
                    'parse_mode': "markdown",
                    'reply_markup': json.dumps({
                        'inline_keyboard': [
                            [{'text': 'رجوع', 'callback_data': "tobot"}],
                        ]
                    })
                })
        else:
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': f"💰] سعر طلبك : {cost}$\n\n◀️] عدد طلبك : {quantity} \n\n*رصيدك لايكفي لطلب {quantity} *\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{'text': 'رجوع + الغاء', 'callback_data': "tobon"}],
                    ]
                })
            })

    if message and text and rshq.get('mode', {}).get(from_id) == "MJK":
        if re.search(r"http|https", text):
            s3r_current = rshq.get('S3RS', {}).get(from_id)
            s3r_current = s3r_current if s3r_current is not None else 1.0
            quantity_for_cost = rshq.get('3dd', {}).get(from_id, {}).get(from_id, 0)
            cost = s3r_current * quantity_for_cost

            bot('sendmessage', {
                'chat_id': chat_id,
                'text': f"] هل أنت متأكد \n\n💰] سعر طلبك : {cost}$\n] ايدي الخدمة : {random.randint(999999, 9999999999999)}\n] الى : [{text}]\n] الكمية : {quantity_for_cost}\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{"text": "موافق ✅", "callback_data": f"YESS|{from_id}"}, {"text": "الغاء ❌", "callback_data": "tobot"}],
                    ]
                })
            })
            rshq[f'LINKS_{from_id}'] = text
            rshq.setdefault('mode', {})[from_id] = "PROG"
            SETJSON(rshq)
        else:
            bot('sendmessage', {
                'chat_id': chat_id,
                'text': "الرجاء إرسال رابط صحيح.\n",
                'parse_mode': "markdown",
            })

    if callback_query and e and e[0] == "YESS" and rshq.get('mode', {}).get(from_id) == "PROG":
        from_id_from_callback = int(e[1])
        # rshq_state = json.loads(read_file("RSHQ/rshq.json")) # Re-read to ensure freshest state - not needed if rshq is global

        s3r_for_order = rshq.get('S3RS', {}).get(from_id_from_callback) # This should be the actual cost
        s3r_for_order = s3r_for_order if s3r_for_order is not None else 0

        inid = rshq.get('IDX', {}).get(from_id_from_callback)
        link_text = rshq.get(f'LINKS_{from_id_from_callback}')
        quantity = rshq.get('3dd', {}).get(from_id_from_callback, {}).get(from_id_from_callback, 0)

        web_for_order = rshq.get('web', {}).get(from_id_from_callback) or rshq.get("sSite")
        key_for_order = rshq.get('key', {}).get(from_id_from_callback) or rshq.get("sToken")

        idreq = None
        if web_for_order and key_for_order:
            try:
                # Assuming 'add' action for placing the order
                request_url = f"https://{web_for_order}/api/v2?key={key_for_order}&action=add&service={inid}&link={link_text}&quantity={quantity}"
                requst_response = requests.get(request_url)
                requst_response.raise_for_status()
                requst = requst_response.json()
                idreq = requst.get('order')
            except requests.exceptions.RequestException as ex:
                print(f"Error placing order: {ex}")

        rnd_order_id = idreq if idreq else random.randint(9999999, 9999999999) # Using the one from the API if available, else a random one

        bot('editmessagetext', {
            'chat_id': chat_id,
            "message_id": message_id,
            'text': f"✅] تم انشاء طلب بنجاح : \n\n🔢] ايدي الطلب : `{rnd_order_id}`\n🌐] تم الطلب الى : [{link_text}]\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "طلب مراجعه الطلب ✅", "callback_data": f"sendrq|{idreq if idreq else 'N/A'}|{rnd_order_id}|{s3r_for_order}"}], # Pass actual api order_id if available
                ]
            })
        })

        # Send message to admin
        bot('sendMessage', {
            'chat_id': admin,
            'text': f"طلب جديد ✅\n- - - - - - - - - - - - - - - - - -\nمعلومات العضو \nايديه : `{from_id}`\nيوزره : @{user}\nاسمه : [{name}](tg://user?id={chat_id})\n\nمعلومات الطلب ~\nايدي الطلب : `{rnd_order_id}`\nالرابط : [{link_text}]\nالعدد: {quantity}\n\nرصيده : {rshq.get('coin', {}).get(str(from_id), 0)}\n- - - - - - - - - - - - - - - - - -\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "ترجيع رصيده", "callback_data": f"ins|{from_id}|{s3r_for_order}"}],
                    [{"text": "طلب تعويض تلقائيا", "callback_data": f"tEwth|{rnd_order_id}"}],
                    [{"text": "تصفير رصيده", "callback_data": f"msft|{from_id}"}],
                ]
            })
        })

        # Send message to channel
        if chnl: # Only send if channel is set
            bot('sendMessage', {
                'chat_id': chnl,
                'text': f"✅ اكتمل طـلب الخدمة بنجاح .\n- - - - - - - - - - - - - - - - - -\nايدي الطلب : `{rnd_order_id}`\nنوع الطلب :{rshq.get('=', {}).get(from_id, 'غير محدد')}\nسعر الطلب :{s3r_for_order}\nالرابط : [{link_text}]\nالعدد {quantity}\nحساب المشتري : [{name}](tg://user?id={chat_id})\nالرقم التسلسلي للطلب : *{rshq.get('bot_tlb', 0) + 1}* \n- - - - - - - - - - - - - - - - - -\n",
                'parse_mode': "markdown",
                'reply_markup': json.dumps({
                    'inline_keyboard': [
                        [{"text": "Social Plus ➕", "url": f"https://t.me/{usrbot_info['result']['username']}"}],
                    ]
                })
            })

        # Update rshq state
        rshq.setdefault("coin", {})[str(from_id)] = rshq.get("coin", {}).get(str(from_id), 0) - s3r_for_order
        rshq.setdefault('S3RS', {})[from_id] = 0 # Reset S3RS for this user
        rshq.setdefault("orders", {}).setdefault(str(from_id), []).append(f"\nا] 🎁 {rshq.get('=', {}).get(from_id)} 🎁\nا] {rnd_order_id}\n")
        rshq.setdefault("order", {})[str(rnd_order_id)] = idreq if idreq else rnd_order_id
        rshq.setdefault("ordn", {})[str(rnd_order_id)] = rshq.get('=', {}).get(from_id) # Storing user-friendly name with the order ID
        rshq.setdefault("sites", {})[str(rnd_order_id)] = web_for_order
        rshq.setdefault("keys", {})[str(rnd_order_id)] = key_for_order
        rshq.setdefault("tlby", {})[str(from_id)] = rshq.get("tlby", {}).get(str(from_id), 0) + 1
        rshq.setdefault("cointlb", {})[str(from_id)] = rshq.get("cointlb", {}).get(str(from_id), 0) + s3r_for_order
        if from_id in rshq.get('3dd', {}): # Check if key exists before accessing
            rshq['3dd'][from_id][from_id] = None
        rshq.setdefault('mode', {})[from_id] = None
        rshq['bot_tlb'] = rshq.get('bot_tlb', 0) + 1
        SETJSON(rshq)

    if callback_query and e and e[0] == "msft" and from_id == admin:
        user_to_reset = e[1]
        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"\nتم تصفير رصيده ✅\nايديه : [{user_to_reset}](tg://user?id={user_to_reset})\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                ]
            })
        })
        rshq.setdefault("coin", {})[user_to_reset] = 0
        SETJSON(rshq)

    if callback_query and e and e[0] == "tEwth" and from_id == admin:
        order_to_refill = e[1]
        site_for_order = rshq.get("sites", {}).get(order_to_refill, current_site)
        key_for_order = rshq.get("keys", {}).get(order_to_refill, current_api_token)

        if site_for_order and key_for_order:
            try:
                requests.get(f"https://{site_for_order}/api/v2?key={key_for_order}&action=refill&order={order_to_refill}")
            except requests.exceptions.RequestException as ex:
                print(f"Error requesting refill: {ex}")

        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"\nتم طلب تعويض تلقائي للطلب\nايدي الطلب `{order_to_refill}`\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                ]
            })
        })

    if callback_query and e and e[0] == "sendrq": # This callback is likely from the user, not admin
        api_order_id = e[1] # Order ID from the API
        user_order_id = e[2] # User's internal order ID
        cost_of_order = float(e[3])

        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"\nتم طلب مراجعه طلبك بنجاح ✅\nايدي الطلب `{user_order_id}`\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "tobot"}],
                ]
            })
        })

        # Notify admin about the review request
        bot('sendMessage', {
            'chat_id': admin,
            'text': f"طلب مراجعه للطلب عزيزي المطور ✨\n- - - - - - - - - - - - - - - - - -\nايدي الطلب (الداخلي) : `{user_order_id}`\nايدي الطلب (الخارجي) : `{api_order_id}`\nالي داز الطلب : [{name}](tg://user?id={from_id})\n- - - - - - - - - - - - - - - - - -\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{"text": "ترجيع رصيده", "callback_data": f"ins|{from_id}|{cost_of_order}"}],
                    [{"text": "طلب تعويض تلقائيا", "callback_data": f"tEwth|{api_order_id}"}],
                ]
            })
        })

    if callback_query and e and e[0] == "ins" and from_id == admin:
        user_to_credit = e[1]
        amount_to_credit = float(e[2])

        bot('EditMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': f"\nتم ارجاع {amount_to_credit} رصيد لحساب [{user_to_credit}](tg://user?id={user_to_credit})\n",
            'parse_mode': "markdown",
            'reply_markup': json.dumps({
                'inline_keyboard': [
                    [{'text': NamesBACK, 'callback_data': "rshqG"}],
                ]
            })
        })
        rshq.setdefault("coin", {})[user_to_credit] = rshq.get("coin", {}).get(user_to_credit, 0) + amount_to_credit
        rshq.setdefault("coinss", {})[user_to_credit] = rshq.get("coinss", {}).get(user_to_credit, 0) + amount_to_credit
        SETJSON(rshq)

def main():
    offset = None
    while True:
        updates_response = get_update(offset)
        if updates_response and updates_response.get('ok'):
            updates = updates_response.get('result', [])
            for update in updates:
                process_update(update)
                offset = update['update_id'] + 1
        time.sleep(1) # Polling interval

if __name__ == '__main__':
    main()
    