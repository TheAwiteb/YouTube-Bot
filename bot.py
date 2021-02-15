import os, sys
from time import sleep
import requests
from random import choice
from string import ascii_lowercase
from threading import Thread
import telebot
from telebot import types
from json import loads
from pytube import YouTube
from youtubesearchpython import VideosSearch, Video

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
🔘اهلا طريقة استعمال البوت بالخاص هي:
🔘يمكنك التنزيل عبر (البحث، والرابط).
🔘يمكنك البحث في (اليوتيوب).
🔘والتنزيل عبر رابط من (اليوتيوب).
🔘طريقة البحث هي كتابة ماتريد البحث عنه.
🔘وطريقة التنزيل عبر ارسال الرابط الذي تود تنزيله.

🔴ملحوظة:
🔘 لطريقة التنزيل بالمجموعة ادخل المجموعة واكتب /help@{botUser}
"""

public_help_msg = f"""
🔘اهلا طريقة استعمال البوت بالمجموعة هي:
🔘يمكنك التنزيل عبر (البحث، والرابط).
🔘يمكنك البحث في (اليوتيوب).
🔘والتنزيل عبر رابط من (اليوتيوب).
🔘طريقة البحث: بحث 'ماتريد البحث عنه'.
🔘وطريقة التنزيل عبر رابط : تنزيل 'الرابط'.
    ▫️مثال التنزيل: تنزيل https://www.youtube.com/watch?v=aMq_W0AYhDk
    ▫️مثال البحث: بحث لمياء المالكي
"""

def send_message_to_admins(text):
    for id_ in admins:
        bot.send_message(id_,f"📢\n🔴هاذي رسالة موجهة للادمنية فقط🔴\n{text}")

mainChaSubscribMsg = f"""
عليك الاشتراك بقناة البوت الاساسية لتتمكن من استخدامه

- @{bot.get_chat(mainCha).username}

‼️ اشترك ثم ارسل /start
"""
def mainCha_subscribed(user_id):
    status = bot.get_chat_member(mainCha, user_id).status
    if status == 'creator' or status == 'administrator' or status == 'member':
        return True
    else:
        return False

def youTubeSearch(user_id, text):
    markup = types.InlineKeyboardMarkup()
    videos = VideosSearch(text, limit = 17).result()['result']
    for video in videos:
        markup.add(types.InlineKeyboardButton(
            text= video['title'], 
            callback_data= f"S Y {user_id} {video['id']}"))
                        #S= Search
                        #Y= YouTube
    markup.add(
        types.InlineKeyboardButton(text='الغاء البحث❗️', 
        callback_data= f"S cancel {user_id}"))
    return markup

def checkLink(chat_id, user_id, message_id, link):
    try:
        yt = YouTube(link)
        downloadMethod(chat_id=chat_id, user_id=user_id, videoID=yt.video_id)
    except:
        bot.send_message(chat_id=chat_id, text="عذرا الرابط لايعمل❗️",reply_to_message_id=message_id)


def downloadMethod(chat_id, user_id, videoID):
    url = "https://www.youtube.com/watch?v="+videoID
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="ملف صوتي 💿", callback_data=f"DM F {user_id} {videoID}"),
                types.InlineKeyboardButton(text="تسجيل صوتي 🎙", callback_data=f"DM V {user_id} {videoID}"))
    markup.add(types.InlineKeyboardButton(text="الغاء التنزيل ⭕️", callback_data=f"DM cancel {user_id}"))
    bot.send_photo(chat_id=chat_id,
                    photo=requests.get(Video.getInfo(url)['thumbnails'][-1]['url']).content,
                    caption=f"<a href='{url}'><b>كيف تريد تنزيل المقطع📥</b></a>",
                    reply_markup=markup,
                    parse_mode="HTML")


def search(chat_id, user_id, message_id, textToSearch, reply_markup):
    markup = reply_markup(user_id, textToSearch)
    if len(markup.to_dict()['inline_keyboard']) == 0:
        msg =f"⛔️عذرا لاتوجد نتائج عن⛔️ '{textToSearch}'"
    else:
        msg = "اختر المقطع الذي تريد تنزيله 📥"
    bot.edit_message_text(chat_id=chat_id,
                                text=msg,
                                message_id=message_id,
                                reply_markup=markup,
                                parse_mode='HTML')


def sureSearch(message_id, chat_id, user_id, textToSearch):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='بحث🔍',callback_data=f"SS Yes {user_id}"),
                types.InlineKeyboardButton(text='الغاء❗️', callback_data=f"SS No {user_id}"))
    bot.send_message(chat_id=chat_id, text=f"اضغط بحث للبحث عن:\n⏺:{textToSearch}",
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


def randomStr(amount):
    return ''.join(choice(ascii_lowercase) for i in range(amount))

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

@bot.message_handler(commands=['start', 'help'])
def commands_handler(message):
    if not mainCha_subscribed(message.from_user.id):
        bot.send_message(chat_id=message.chat.id, reply_to_message_id=message.id,
                        text=mainChaSubscribMsg, 
                        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='𝕔𝕙𝕒.', url=f"https://telegram.me/{bot.get_chat(mainCha).username}")))
    else:
        if message.chat.type == 'private':
            bot.send_message(chat_id=message.chat.id,
                            text=private_help_msg,
                            reply_to_message_id= message.id,
                            reply_markup=dev_addBot(),
                            parse_mode='HTML')
        else:
            bot.send_message(chat_id=message.chat.id,
                            text=public_help_msg,
                            reply_to_message_id= message.id,
                            reply_markup=dev_addBot(),
                            parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(func=lambda msg: True ,content_types= ['text'])
def message_handler(message):
    if not mainCha_subscribed(message.from_user.id):
        bot.send_message(chat_id=message.chat.id, reply_to_message_id=message.id,
                        text=mainChaSubscribMsg, 
                        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='𝕔𝕙𝕒.', url=f"https://telegram.me/{bot.get_chat(mainCha).username}")))
    else:
        #الرجاء عدم حذف حقوق مطور السور
        if message.text.split()[0] in ['سورس','السورس']:
            bot.send_message(chat_id=message.chat.id, reply_to_message_id=message.id,
                            text="https://github.com/Awiteb/YouTube-Bot\n\ndev:@AWWWZ  cha:@Awiteb_source ⌨️", parse_mode="HTML")
        elif message.text.split()[0] == 'بحث':
            sureSearch(message_id=message.id, chat_id=message.chat.id, user_id=message.from_user.id, textToSearch=message.text.replace('بحث ',''))
        elif message.text.split()[0] == 'تنزيل':
            checkLink(chat_id=message.chat.id, message_id=message.id, user_id=message.from_user.id, link=message.text.split()[1])
        else:
            if message.chat.type == 'private':
                if 'youtube' in message.text.split()[0] or 'youtu' in message.text.split()[0]:
                    checkLink(chat_id=message.chat.id, message_id=message.id, user_id=message.from_user.id, link=message.text.split()[0])
                else:
                    sureSearch(message_id=message.id, chat_id=message.chat.id, user_id=message.from_user.id, textToSearch=message.text)
            else:
                pass


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if not mainCha_subscribed(call.from_user.id):
        if call.message.photo == None:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                            text=mainChaSubscribMsg, 
                            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='𝕔𝕙𝕒.',
                                                                            url=f"https://telegram.me/{bot.get_chat(mainCha).username}")))
        else:
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id
                        ,media=types.InputMediaPhoto(call.message.photo[0].file_id),
                        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='⭕️ الرجاء الاشتراك بقناة البوت',
                                                                            url=f"https://telegram.me/{bot.get_chat(mainCha).username}")))

    else:
        callbackData = str(call.data).split()
        print(f"call back ->{callbackData}\nLen ->{len(call.data)}")
        request_interface = int(callbackData[2])
        button = callbackData[1]
        interface = callbackData[0]
        if request_interface == call.from_user.id:
            if interface == 'SS': #SureSearch
                textToSearch = call.message.text.replace('اضغط بحث للبحث عن:\n⏺:', '').strip()
                if button == 'Yes':
                    search(chat_id=call.message.chat.id, user_id=request_interface,
                                        textToSearch=textToSearch,message_id=call.message.message_id,reply_markup= youTubeSearch)
                elif button == 'No':
                    bot.edit_message_text(text="تم الغاء البحث✔️",chat_id=call.message.chat.id,
                                        message_id=call.message.message_id, reply_markup=dev_cha())
            elif interface == 'S': #Search
                if button == 'Y':
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    downloadMethod(chat_id=call.message.chat.id, user_id=request_interface,
                                        videoID=callbackData[3])
                elif button == 'cancel':
                    bot.edit_message_text(text="تم الغاء البحث ❗️", message_id=call.message.message_id, chat_id=call.message.chat.id,)
            elif interface == 'DM': #DownloadMethod
                if button == 'cancel':
                    bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id
                        ,media=types.InputMediaPhoto(call.message.photo[0].file_id),
                        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                        text='🛑 تم الغاء التنزيل', callback_data=f"audio cancel {request_interface}")))
                else:
                    bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id
                                            ,media=types.InputMediaPhoto(call.message.photo[0].file_id),
                                            reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                                text="جاري التنزيل 🔄",callback_data=f"audio Dling {request_interface}")))
                                                                                #Dling = Downloading
                    try:
                        yt = YouTube(f"https://www.youtube.com/watch?v={callbackData[3]}")
                        title = yt.title
                        channel = yt.author
                        filename = randomStr(amount=9)
                        yt.streams.filter(only_audio=True).first().download(filename=f"{filename}")
                        with open(f"{filename}.mp4",mode="rb") as f:  
                            if button == 'F': #file
                                Thread(target=make_action, args=(call.message.chat.id, "upload_document", 5)).start()
                                bot.send_audio(chat_id=call.message.chat.id,audio=f.read(),
                                            caption=f'<a href="tg://user?id={botID}">{botName}🎧</a>', parse_mode="HTML",
                                            performer=channel,title=title, thumb=requests.get(f"https://api.telegram.org/file/bot{token}/{bot.get_file(call.message.photo[0].file_id).file_path}").content)
                            elif button == 'V': #Voise
                                Thread(target=make_action, args=(call.message.chat.id, "upload_video_note", 5)).start()
                                bot.send_voice(chat_id=call.message.chat.id, voice=f.read(),
                                                caption=f'<a href="tg://user?id={botID}">{title}</a>', parse_mode="HTML")
                    except Exception as e:
                        if str(e) == "A request to the Telegram API was unsuccessful. Error code: 413. Description: Request Entity Too Large":
                            downloadErrorMsg = "عذرا لقد تجاوز حجم الملف 50 MG❗️"
                        else:
                            downloadErrorMsg = 'مشكلة بالتنزيل 🛑'
                        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id
                                        ,media=types.InputMediaPhoto(call.message.photo[0].file_id),
                                        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                            text=downloadErrorMsg, callback_data=f"audio dl-problem {request_interface}")))
                                                                            #dl-problem = Download problem 
                    else:
                        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id
                                        ,media=types.InputMediaPhoto(call.message.photo[0].file_id),
                                        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                            text="تم التنزيل ✅",callback_data=f"audio dld {request_interface}")))
                                                                        #dld = Downloaded
                    try:
                        os.remove(f"{filename}.mp4")
                    except:
                        pass
            elif interface == 'audio':
                if button == 'Dling':
                    bot.answer_callback_query(callback_query_id=call.id,
                                show_alert=True,
                                text=f"جاري تنزيل المقطع الصوتي 🔘")
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


# Run bot
while True:
    try:
        print(f"Start {bot.get_me().first_name}{' '+bot.get_me.last_name if bot.get_me().last_name != None else ''}")
        bot.polling(none_stop=True, interval=0, timeout=0)
    except Exception as e:
        send_message_to_admins(text= f"عندك مشكلة بالكود\nتعريف المشكلة:\n{e}\n-")
        sleep(10)
