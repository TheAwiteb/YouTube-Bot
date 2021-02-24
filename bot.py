# -*- coding: utf-8 -*-

import os, sys
from time import sleep
from datetime import datetime
import requests
from random import choice
from string import ascii_lowercase
from threading import Thread
import telebot
from telebot import types
from json import loads
from pytube import YouTube, Playlist
from youtubesearchpython import VideosSearch, Video, PlaylistsSearch

# get bot data from json file #
while True:
    if os.path.lexists("./config.json"):
        try:
            with open('config.json','r') as botData:
                data = loads(botData.read())
                token = data['token']
                dev_id = data['devID']
                admins = data['admins']
                mainCha = data['mainCha']
                break
        except Exception as e:
            print("Sorry, the data syntax in config.json has a problem, let's get back Reframe it.!,")
            os.remove("./config.json")
            continue
    else:
        with open('config.json','w+') as newJson:
            print("Done make new json file name 'config.json', The bot token and admin id, will be saved in this file.")
            dev_id = int(input("Enter dev id: "))
            token = input("Enter bot token: ")
            amount = int(input("How many admin you want add: "))
            mainCha = int(input("Enter cha id: "))
            admins = []
            admins.append(dev_id)
            for i in range(amount):
                i =+1
                admins.append(int(input(f"Enter admin number {i} of {amount}: ")))
            newJson.write('{"token":"%s","devID":%i,"admins":%s,"mainCha":"%s"}' %(token, dev_id, admins, mainCha))
            break


bot = telebot.TeleBot(token=token)
botUser = bot.get_me().username
botID = bot.get_me().id
botName = bot.get_me().first_name

#solve chat admin not found
try:
    dev_url = f"https://t.me/{bot.get_chat(dev_id).username}"
except:
    print(f"Admin id is {dev_id} if id is true send a message to the bot and then restart it.")
    sys.exit(1)

private_help_msg = f"""
🔘اهلا طريقة استعمال بوت اليوتيوب بالخاص هي:
🔘يمكنك التنزيل عبر (البحث، والرابط).
🔘يمكنك البحث عن (مقاطع + قوائم تشغيل).
🔘والتنزيل عبر رابط (مقاطع + قوائم تشغيل).
🔘طريقة البحث هي كتابة ماتريد البحث عنه.
🔘وطريقة التنزيل عبر ارسال الرابط الذي تود تنزيله.

🔴ملحوظة:
🔘 لطريقة التنزيل بالمجموعة ادخل المجموعة واكتب 
/help@{botUser}
⁦
"""

public_help_msg = f"""
🔘اهلا طريقة استعمال بوت اليوتيوب بالمجموعة هي:
🔘يمكنك التنزيل عبر (البحث، والرابط).
🔘يمكنك البحث عن (مقاطع + قوائم تشغيل).
🔘والتنزيل عبر رابط (مقاطع + قوائم تشغيل).
🔘طريقة البحث ⬅️ بحث 'ماتريد البحث عنه'.
🔘وطريقة التنزيل عبر رابط ⬅️ تنزيل 'الرابط'.

    ▫️مثال التنزيل⬅️ تنزيل https://www.youtube.com/watch?v=aMq_W0AYhDk
    ▫️مثال البحث: بحث زينة عماد
⁦
"""

def send_message_to_admins(text):
    for id_ in admins:
        bot.send_message(id_,f"📢\n🔴هاذي رسالة موجهة للادمنية فقط🔴\n{text}")

mainChaSubscribMsg = lambda user_id, first_name:f"""
'<a href="tg://user?id={user_id}">{first_name}</a>'
عليك الاشتراك بقناة البوت الاساسية لتتمكن من استخدامه

- @{bot.get_chat(mainCha).username}

‼️ اشترك ثم ارسل /start
⁦
"""
bot_on = True
ofMsg = "عذرا البوت متوقف مؤقتاَ 🙁"
printOFmsg = False

def mainCha_subscribed(object_, printMsg:bool):
    if str(type(object_)) == "<class 'telebot.types.CallbackQuery'>":
        obType = 'call'
        message_id = object_.message.id
        chat_id = object_.message.chat.id
    else:
        obType = 'message'
        chat_id = object_.chat.id
        message_id = object_.id
    user_id = object_.from_user.id
    status = bot.get_chat_member(mainCha, user_id).status
    if status != 'left':
        return True
    else:
        if printMsg:
            if obType == 'call' and object_.message.photo != None:
                bot.edit_message_media(chat_id=chat_id, message_id=message_id,
                            media=types.InputMediaPhoto(object_.message.photo[0].file_id),
                            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text=f'⭕️ يجب الاشتراك بقناة البوت لاستعماله {object_.from_user.first_name}',
                                                                                url=f"https://telegram.me/{bot.get_chat(mainCha).username}")))
            else:
                if obType == 'call':
                    bot.delete_message(chat_id=chat_id,message_id=message_id)
                else:
                    pass
                bot.send_message(chat_id=chat_id, reply_to_message_id=None if obType == 'call' else message_id,
                                text=mainChaSubscribMsg(user_id=user_id, first_name=object_.from_user.first_name),parse_mode='HTML',
                                reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='𝕔𝕙𝕒.', url=f"https://telegram.me/{bot.get_chat(mainCha).username}")))
        else:
            pass
    return False

def youTubeVidSearch(user_id, text):
    markup = types.InlineKeyboardMarkup()
    videos = VideosSearch(text, limit = 17).result()['result']
    for video in videos:
        markup.add(types.InlineKeyboardButton(
            text= video['title'],
            callback_data= f"YS V {user_id} {video['id']}"))
                            #YS= YouTube Search
                            #V= Video
    markup.add(
        types.InlineKeyboardButton(text='الغاء البحث❗️', 
        callback_data= f"YS cancel {user_id}"))
    return markup

def youTubeListSearch(user_id, text):
    markup = types.InlineKeyboardMarkup()
    lists = PlaylistsSearch(text, limit = 17).result()['result']
    for list in lists:
        markup.add(types.InlineKeyboardButton(
            text= list['title'],
            callback_data= f"YS L {user_id} {list['id']}"))
                            #YS= YouTube Search
                            #L= list
    markup.add(
        types.InlineKeyboardButton(text='الغاء البحث❗️', 
        callback_data= f"YS cancel {user_id}"))
    return markup

def checkVidLink(message, link):
    chat_id= message.chat.id
    user_id=message.from_user.id
    message_id=message.id
    try:
        yt = YouTube(link)
        downloadMethod(chat_id=chat_id, user_id=user_id, vid_id=yt.video_id, amount=None)
    except:
        bot.send_message(chat_id=chat_id, text=" رابط الفيديو لايعمل❗️",reply_to_message_id=message_id)


def checkListLink(object_, link):
    if str(type(object_)) == "<class 'telebot.types.CallbackQuery'>":
        message_id = object_.message.id
        chat_id = object_.message.chat.id
    else:
        chat_id = object_.chat.id
        message_id = object_.id
    user_id = object_.from_user.id
    try:
        yt = Playlist(link)
        markup = types.InlineKeyboardMarkup()
        vidCount = len(yt.video_urls)
        numbers = divide(number=vidCount, amount= 5 if vidCount >100 else 4)
        for idx in range(len(numbers) - 1):
            if idx % 2 == 0:
                markup.add(types.InlineKeyboardButton(text=f"{numbers[idx] if numbers[idx] != 0 else 1}.", callback_data= f"PL {numbers[idx] if numbers[idx] != 0 else 1} {user_id} {yt.playlist_id}"),
                    types.InlineKeyboardButton(text=f"{numbers[idx+1] if numbers[idx+1] != 0 else 1}.", callback_data= f"PL {numbers[idx+1] if numbers[idx+1] != 0 else 1} {user_id} {yt.playlist_id}"))
                                                                                        #lt = list
            else:
                pass        
        bot.send_message(chat_id=chat_id, text=f"- اسم القائمة {yt.title}\n- عدد الفيديوهات {vidCount}\n\nكم عنصر تريد تنزيله من القائمة ؟ 📥\n⁦",
                        reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        bot.send_message(chat_id=chat_id, text=" رابط قائمة التشغيل لايعمل❗️",reply_to_message_id=message_id)


def sendVid(call, vid_id, method, is_list):
    #method 'F' = file(mp3)
    #method 'V' = Voise
    try:
        yt = YouTube("https://www.youtube.com/watch?v="+vid_id)
        title = yt.title
        author = yt.author
        filename = randomStr(length=9)
        yt.streams.filter(only_audio=True).first().download(filename=f"{filename}")
        
        with open(f"{filename}.mp4",mode="rb") as f:  
            if method == 'F': #file
                Thread(target=make_action, args=(call.message.chat.id, "upload_document", 5)).start()
                bot.send_audio(chat_id=call.message.chat.id,audio=f.read(),
                                caption=f'<a href="tg://user?id={botID}">{botName}🎧</a>', parse_mode="HTML",
                                performer=author,title=title, thumb=requests.get(
                                f"https://api.telegram.org/file/bot{token}/{bot.get_file(call.message.photo[0].file_id).file_path}").content)
            elif method == 'V': #Voise
                Thread(target=make_action, args=(call.message.chat.id, "upload_video_note", 5)).start()
                bot.send_voice(chat_id=call.message.chat.id, voice=f.read(),
                                caption=f'<a href="tg://user?id={botID}">{title}</a>', parse_mode="HTML")
    except Exception as e:
        if is_list:
            if 'private' in str(e):
                vidStute = 'خاص'
            elif 'unavailable' in str(e):
                vidStute = 'محذوف'
            elif '413' in str(e):
                vidStute = 'تجاوز حجمه ال 50 MG'
            else:
                vidStute = 'لايمكن تنزيله'
            bot.send_message(chat_id=call.message.chat.id, reply_to_message_id=call.message.id,
                                text=f"🔺 يوجد فيديو {vidStute} في هذه القائمة")
        else:
            if '413' in str(e):
                downloadErrorMsg = "عذرا لقد تجاوز حجم الملف 50 MG❗️"
            else:
                downloadErrorMsg = 'مشكلة بالتنزيل 🛑'
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id,
                                    media=types.InputMediaPhoto(call.message.photo[0].file_id),
                                        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                            text=downloadErrorMsg, callback_data=f'answer dl-problem {call.from_user.id}',url="https://www.youtube.com/watch?v="+vid_id)))
                                                                                #dl-problem = Download problem 
    try:
        os.remove(f"{filename}.mp4")
    except:
        pass

def downloadMethod(chat_id, user_id, vid_id, amount):
    if not amount:
        url = "https://www.youtube.com/watch?v="+vid_id
        caption = f"<a href='{url}'><b>كيف تريد تنزيل الفيديو</b></a>"
        photo = requests.get(Video.getInfo(url)['thumbnails'][-1]['url']).content
    else:
        amount = int(amount)
        url = "https://www.youtube.com/playlist?list="+vid_id
        if amount == 1:
            nameOFamount = "فيديو"
        elif amount == 2:
            nameOFamount = "فيديوهين"
        elif amount <= 10:
            nameOFamount = f"{amount} فيديوهات"
        else:
            nameOFamount = f"{amount} فيديو"
            
        caption = f"<a href='{url}'><b>كيف تريد تنزيل {nameOFamount}  من قائمة التشغيل📥</b></a>"
        try:
            photo = requests.get(Video.getInfo(Playlist(url).video_urls[0])['thumbnails'][-1]['url']).content
        except:
            photo = requests.get("https://i.pinimg.com/originals/09/0c/06/090c0658afb2350efff9c2ac705d5fe9.jpg").content
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="ملف صوتي 💿", callback_data=f"DM F {user_id} {vid_id} {amount}"),
                types.InlineKeyboardButton(text="تسجيل صوتي 🎙", callback_data=f"DM V {user_id} {vid_id} {amount}"))
    markup.add(types.InlineKeyboardButton(text="الغاء التنزيل ⭕️", callback_data=f"DM cancel {user_id}"))
    bot.send_photo(chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    reply_markup=markup,
                    parse_mode="HTML")


def search(chat_id, user_id, message_id, textToSearch, reply_markup, searchToVid):
    markup = reply_markup(user_id, textToSearch)
    if len(markup.to_dict()['inline_keyboard']) == 0:
        msg =f"⛔️عذرا لاتوجد نتائج عن⛔️ '{textToSearch}'"
    else:
        msg = f"اختر {'الفيديو' if searchToVid else 'القائمة'} الذي تريد {'تنزيله' if searchToVid else 'تنزيلها'} 📥"
    bot.edit_message_text(chat_id=chat_id,
                                text=msg,
                                message_id=message_id,
                                reply_markup=markup,
                                parse_mode='HTML')

def searchVidORlist(message, textToSearch):
    message_id = message.id
    chat_id = message.chat.id
    user_id = message.from_user.id
    can_install_list = message.chat.type == 'private' or user_id in [id.user.id for id in bot.get_chat_administrators(chat_id)] or user_id in admins
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='فيديوهات📹',callback_data=f"VL V {user_id}"),
                types.InlineKeyboardButton(text=f"قوائم تشغيل💾 {'' if can_install_list else '❌'}", callback_data=f"{'VL' if can_install_list else 'answer'} L {user_id}"))
    markup.add(types.InlineKeyboardButton(text='الغاء❗️', callback_data=f"VL No {user_id}"))
    bot.send_message(chat_id=chat_id, text=f"كيف تريد البحث عن:\n⏺:{textToSearch}",
                    reply_markup=markup, reply_to_message_id=message_id)


def dev_addBot():
    markup = types.InlineKeyboardMarkup()
    devButton = types.InlineKeyboardButton(text='𝕕𝕖𝕧.', url=dev_url)
    addBotButton = types.InlineKeyboardButton(text='𝕒𝕕𝕕𝔹𝕠𝕥.', url=f"https://telegram.me/{botUser}?startgroup=new")
    markup.add(devButton)
    markup.add(addBotButton)
    return markup

def dev_cha():
    markup = types.InlineKeyboardMarkup()
    devButton = types.InlineKeyboardButton(text='𝕕𝕖𝕧.', url=dev_url)
    chaButton = types.InlineKeyboardButton(text='𝕔𝕙𝕒.', url=f"https://telegram.me/{bot.get_chat(mainCha).username}")
    markup.add(devButton)
    markup.add(chaButton)
    return markup


def randomStr(length):
    return ''.join(choice(ascii_lowercase) for i in range(length))

def divide(number, amount):
    res = []
    res.append(number)
    for i in range(amount):
        number //=2
        res.append(number)
    return res

def make_action(chat_id, action, timeout):
    #typing for text messages
    #upload_photo for photos
    #upload_video for videos
    #record_video for video recording
    #upload_audio for audio files
    #record_audio for audio file recording
    #upload_document for general files
    #find_location for location data
    #upload_video_note for video notes
    #record_video_note for video note recording
    bot.send_chat_action(chat_id=chat_id, action=action, timeout=timeout)


def pingCommand(message):
    speed = int(datetime.now().timestamp() - datetime.fromtimestamp(message.date).timestamp())
    if speed < 3:
        typeSpeed = "رائعة 👌🏼"
    elif speed <= 8:
        typeSpeed = "جيدة  🙁"
    else:
        typeSpeed = "سيئة 👎🏼"
        
    if speed == 0:
        speed = 'صفر'
        timeName = ''
    elif speed == 1:
        speed = 'ثانية'
        timeName = ''
    elif speed == 2:
        speed = "ثانيتين"
        timeName = ''
    elif speed <= 10:
        timeName = 'ثواني'
    else:
        timeName = 'ثانية'
    bot.reply_to(message, text=f"سرعة البوت {typeSpeed}\nالسرعة: {speed} {timeName}\n⁦", reply_markup=
                    types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='𝕔𝕙𝕒.', url=f"https://telegram.me/{bot.get_chat(mainCha).username}")))

@bot.edited_message_handler(commands=['start','help'])
@bot.message_handler(commands=['ping','start','help'])
def commands_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    msg_txt = message.text
    chat_private = True if message.chat.type == 'private' else False
    if bot_on or user_id in admins:
        if not mainCha_subscribed(object_=message, printMsg=True):
            pass
        else:
            if msg_txt.lower().startswith('/ping'):
                pingCommand(message)
            else:
                bot.send_message(chat_id=chat_id,
                            text=private_help_msg if chat_private else public_help_msg,
                            reply_to_message_id= message.id,
                            reply_markup=dev_addBot(),
                            parse_mode='HTML', disable_web_page_preview=True)
    else:
        if printOFmsg and chat_private:
            bot.send_message(chat_id=chat_id, text=ofMsg, reply_to_message_id=message.id,
                                disable_notification= True, reply_markup=dev_cha())


@bot.edited_message_handler(func=lambda msg: True ,content_types= ['text'])
@bot.message_handler(func=lambda msg: True ,content_types= ['text'])
def message_handler(message):
    user_id = message.from_user.id
    msg_txt = message.text
    chat_id = message.chat.id
    chat_private = True if message.chat.type == 'private' else False
    if bot_on or user_id in admins:
        if chat_private and not mainCha_subscribed(object_=message, printMsg=False):
            mainCha_subscribed(object_=message, printMsg=True) #اذ لم يكن مشترك وفي الخاص ارسله
        else: # اذا كان مشترك او لم يكن بالخاص
            
            #الرجاء عدم حذف حقوق مطور السورس
            if msg_txt.split()[0] in ['سورس','السورس'] and mainCha_subscribed(object_=message, printMsg=True):  #الرجاء عدم حذف حقوق مطور السورس
                bot.send_message(chat_id=chat_id, reply_to_message_id=message.id,
                                    text="https://github.com/Awiteb/YouTube-Bot\n\ndev:@AWWWZ  cha:@Awiteb_source ⌨️", parse_mode="HTML") #الرجاء عدم حذف حقوق مطور السورس
            
            elif msg_txt.split()[0] == 'بحث' and len(msg_txt.split()) != 1 and mainCha_subscribed(object_=message, printMsg=True):
                searchVidORlist(message=message, textToSearch=msg_txt.replace('بحث ',''))
            
            elif msg_txt.split()[0] == 'تنزيل' and len(msg_txt.split()) != 1 and mainCha_subscribed(object_=message, printMsg=True):
                if 'youtube' in msg_txt.lower().split()[0] or 'youtu' in msg_txt.lower().split()[1]:
                    if 'playlist?list=pl' in msg_txt.lower().split()[1]:
                        if chat_private:
                            checkListLink(object_=message, link=msg_txt.split()[1])
                        else:
                            if user_id in [id.user.id for id in bot.get_chat_administrators(chat_id)] or user_id in admins:
                                    checkListLink(object_=message, link=msg_txt.split()[1])
                            else:
                                bot.send_message(chat_id=chat_id, reply_to_message_id=message.id,
                                    text="🔺عذرا لتنزيل قائمة يجب ان تكون احد المشرفين\n ⁦")
                    else:
                        checkVidLink(message=message, link=msg_txt.split()[0])
                else:
                    pass
            elif msg_txt in ['سرعة البوت', 'سرعه البوت'] and mainCha_subscribed(object_=message, printMsg=True):
                pingCommand(message)
            else:
                if chat_private:
                    if 'youtube' in msg_txt.lower().split()[0] or 'youtu' in msg_txt.lower().split()[0]:
                        if 'playlist?list=pl' in msg_txt.lower().split()[0]:
                            checkListLink(object_=message, link=msg_txt.split()[0])
                        else:
                            checkVidLink(message=message, link=msg_txt.split()[0])
                    else:
                        searchVidORlist(message=message, textToSearch=msg_txt)
                else:
                    pass
    else:
        if printOFmsg and chat_private:
            bot.send_message(chat_id=chat_id, text=ofMsg, reply_to_message_id=message.id,
                                disable_notification= True, reply_markup=dev_cha())
        else:
            pass

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_txt = call.message.text
    msg_id = call.message.message_id
    if bot_on or user_id in admins:
        if not mainCha_subscribed(object_=call, printMsg=True):
            pass
        else:
            callbackData = str(call.data).split()
            request_interface = int(callbackData[2])
            button = callbackData[1]
            interface = callbackData[0]
            if user_id == request_interface:
                if interface == 'VL': #searchVidORlist
                    textToSearch = msg_txt.replace('كيف تريد البحث عن:\n⏺:', '').strip()
                    if button == 'V':
                        search(chat_id=chat_id, user_id=request_interface,
                                textToSearch=textToSearch,message_id=msg_id,
                                    reply_markup= youTubeVidSearch, searchToVid=True)
                    elif button == 'L':
                        search(chat_id=chat_id, user_id=request_interface,
                                textToSearch=textToSearch,message_id=msg_id,
                                    reply_markup= youTubeListSearch, searchToVid=False)
                    else:
                        bot.edit_message_text(text="تم الغاء البحث✔️",chat_id=chat_id,
                                            message_id=msg_id, reply_markup=dev_cha())
                elif interface == 'YS': #Search
                    if button == 'V':
                        bot.delete_message(chat_id=chat_id, message_id=msg_id)
                        downloadMethod(chat_id=chat_id, user_id=request_interface,
                                            vid_id=callbackData[3], amount=None)
                    elif button == 'L':
                        bot.delete_message(chat_id=chat_id, message_id=msg_id)
                        checkListLink(object_=call, link="https://www.youtube.com/playlist?list="+callbackData[3])
                    elif button == 'cancel':
                        bot.edit_message_text(text="تم الغاء البحث ❗️", message_id=msg_id, chat_id=chat_id)
                elif interface == 'PL': #playList
                    bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    downloadMethod(chat_id=chat_id, user_id=request_interface, vid_id=callbackData[3],
                                    amount=button)
                elif interface == 'DM': #DownloadMethod
                    if button == 'delete':
                        bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    elif button == 'cancel':
                        bot.edit_message_media(chat_id=chat_id, message_id=msg_id,
                            media=types.InputMediaPhoto(call.message.photo[0].file_id),
                            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                            text='🛑 تم الغاء التنزيل', callback_data=f'answer cancel {request_interface}')).add(
                            types.InlineKeyboardButton(text="⭕️مسح الرسالة", callback_data=f"DM delete {request_interface}")))
                    else:
                        bot.edit_message_media(chat_id=chat_id, message_id=msg_id,
                                                media=types.InputMediaPhoto(call.message.photo[0].file_id),
                                                reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                                    text="جاري التنزيل 🔄",callback_data=f'answer Dling {request_interface}')))
                                                                                    #Dling = Downloading
                        if callbackData[3].startswith('PL'):
                            if call.message.chat.type != 'private' and int(callbackData[4]) > 8:
                                bot.send_message(chat_id=chat_id, text=f"🔺عذرا لايمكن تنزيل ال{callbackData[4]} جميعهم سوف يتم تنزيل 8 صوتيات فقط\nيمكن تنزيل ال {callbackData[4]}  بخاص البوت\n⁦", 
                                                    reply_to_message_id=msg_id,
                                                        reply_markup=dev_cha())
                                limt = 8
                            else:
                                limt = int(callbackData[4])
                            for link in Playlist("https://www.youtube.com/playlist?list="+callbackData[3]).video_urls[:limt - 1]:
                                Thread(target=sendVid,args=(call,link.replace('https://www.youtube.com/watch?v=', ''),button, True)).start()
                            doneDl = True
                        else:
                            sendVid(call=call,vid_id=callbackData[3], method=button,is_list=False)
                            doneDl = True
                        if doneDl:
                            bot.edit_message_media(chat_id=chat_id, message_id=msg_id,
                                            media=types.InputMediaPhoto(call.message.photo[0].file_id),
                                                reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                                    text="تم التنزيل ✅",callback_data=f'answer dld {request_interface}')).add(
                                            types.InlineKeyboardButton(text="مسح الرسالة ⭕️", callback_data=f"DM delete {request_interface}")))
                                                                        #dld = Downloaded
                elif interface == 'answer':
                    if button == 'Dling':
                        bot.answer_callback_query(callback_query_id=call.id,
                                    show_alert=True,
                                    text=f"جاري تنزيل المقطع الصوتي 🔘")
                    elif button == 'L':
                        bot.answer_callback_query(callback_query_id=call.id,
                                    show_alert=True,
                                    text=f"🔺لايمكنك البحث عن قوائم التشغيل\nلانك لست مشرف بالمجموعة")
                    elif button == 'dld':
                        bot.answer_callback_query(callback_query_id=call.id,
                                    show_alert=True,
                                    text=f"تم التنزيل بنجاح 🔘")
                    elif button == 'dl-problem':
                        bot.answer_callback_query(callback_query_id=call.id,
                                    show_alert=True,
                                    text='🛑عذرا توجد مشكلة بالتنزيل')
                    elif button == 'cancel':
                        bot.answer_callback_query(callback_query_id=call.id,
                                    show_alert=True,
                                    text='🔘 تم الالغاء بنجاح')
            else:
                bot.answer_callback_query(callback_query_id=call.id,
                                    show_alert=True,
                                    text=f"عذرا القائمة ليست لك!🚫")
    else:
        if printOFmsg and call.message.chat.type == 'private':
            bot.send_message(chat_id=chat_id, text=ofMsg, reply_to_message_id=call.message.id,
                                disable_notification= True, reply_markup=dev_cha())


# Run bot
while True:
    try:
        print(f"Start {bot.get_me().first_name}{' '+bot.get_me.last_name if bot.get_me().last_name != None else ''}")
        bot.polling(none_stop=True, interval=0, timeout=0)
    except Exception as e:
        send_message_to_admins(text= f"عندك مشكلة بالكود\nتعريف المشكلة:\n{e}\n⁦")
        sleep(10)
