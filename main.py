from mpegdash.parser import MPEGDASHParser
from button_build import ButtonMaker
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import requests
from getKeys import getKeyss
from getPSSH import getPSSHs
from time import sleep
from download import down, decr
import os, glob
from pyrogram import Client

dic = {}
proxy1 = dict(scheme="socks5", hostname="216.241.193.166", port=8111) 

client = Client(
    name="pyrogrammm",
    api_id=17872567,
    api_hash='6aea250af9d83f85a9adc8e34705415a',
    bot_token='5452169338:AAGCq9zOWxcBz_YNp73F4dV4JIxDDfWT7Dc',
    no_updates=True,
    proxy=proxy1
)

app = ApplicationBuilder().token("5452169338:AAGCq9zOWxcBz_YNp73F4dV4JIxDDfWT7Dc").build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("damn it!", quote=True)

async def help(update, context):
    await update.message.reply_text('''
<b>Send them in this format:</b>

[<code>mpd_link</code>] [<code>license_url</code>]
    
<b>Eg:</b> <i>https://cdn.bitmovin.com/content/assets/art-of-motion_drm/mpds/11331.mpd https://cwip-shaka-proxy.appspot.com/no_auth</i>  
''', parse_mode="HTML", quote=True)

async def calls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.split('_')[1] == 'vid':
        global vid_id
        vid_id = query.data.split('_', maxsplit=2)[-1]
        await query.edit_message_text('''<b>
Chose audio quality for download
    </b>''', parse_mode='HTML', reply_markup=aud)
    else:
        aud_id = query.data.split('_', maxsplit=2)[-1]
        await query.edit_message_text("<i>Downloading...</i>", parse_mode='HTML')
        user = query.from_user.id
        try:
            dic[user] += 1
        except:
            dic.update({user: 1})
        print(dic)
        result = await down(vid_id, aud_id, mpdURL, user)
        if result == 'OK':
            await query.edit_message_text("<i>Decrypting video...</i>", parse_mode='HTML')
            result2 = await decr(keys)
            if result2 == 'OK':
                await query.edit_message_text("<i>Uploading video...</i>", parse_mode='HTML')
                await send()
                await query.delete_message()

def cleanup(path):
    leftover_files = glob.glob(path + '/*.mp4', recursive=True)
    mpd_files = glob.glob(path + '/*.mpd', recursive=True)
    leftover_files = leftover_files + mpd_files
    for file_list in leftover_files:
        try:
            os.remove(file_list)
        except OSError:
            print(f"Error deleting file: {file_list}")

async def send():
    try:await client.start()
    except: pass
    #await msg.reply_video(r'final.mp4', write_timeout=240, supports_streaming=True)
    await client.send_video(msg.chat_id, open('final.mp4', 'rb'),supports_streaming=True, reply_to_message_id=msg.id)
    try:await client.stop()
    except:pass
    cleanup(os.getcwd())

async def getButtons(message):
    uid = message.from_user.id
    mpd = MPEGDASHParser.parse("manifest.mpd")
    v_buttons = ButtonMaker()
    a_buttons = ButtonMaker()
    for period in mpd.periods:
        for adapt_set in period.adaptation_sets:
            content_type = adapt_set.mime_type
            if adapt_set.mime_type == "video/mp4":
                for h in adapt_set.representations:
                    print(h.height)
                    v_buttons.sbutton(f"{h.height}p", f"{uid}_vid_{h.id}")
            else:
                for q in adapt_set.representations:
                    a_buttons.sbutton(f"{q.id}", f"{uid}_aud_{q.id}")
    vid = v_buttons.build_menu(1)
    # await message.reply_html("<b>Chose video quality</b>", reply_markup=vid)
    global aud
    aud = a_buttons.build_menu(1)
    # await message.reply_html("<b>Chose audio quality</b>", reply_markup=aud)
    return vid, aud

async def input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global msg
    msg = update.message
    if msg.text[-3:] == "mpd":
        await msg.reply_text('''
<b>Send them in this format:</b>

[<code>mpd_link</code>] [<code>license_url</code>] [<code>user_agent_header</code>]
    
<b>Eg:</b> <i>https://cdn.bitmovin.com/content/assets/art-of-motion_drm/mpds/11331.mpd https://cwip-shaka-proxy.appspot.com/no_auth</i> <code>Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36</code>  
''', parse_mode="HTML", quote=True)
    elif len(str(msg.text).split(maxsplit=1)) == 2:
        # message.reply('<b>Keys are being extracting . . .</b>')
        message1 = await msg.reply_html('<b>Keys are being extracted . </b>', quote=True)
        sleep(0.5)
        message1 = await message1.edit_text('<b>Keys are being extracted . .</b>', parse_mode='HTML')
        sleep(0.5)
        message1 = await message1.edit_text('<b>Keys are being extracted . . .</b>', parse_mode='HTML')
        sleep(0.25)
        global mpdURL
        mpdURL, lic = str(msg.text).split(maxsplit=1)
        manifest = requests.get(mpdURL).text
        with open("manifest.mpd", 'w') as manifest_handler:
            manifest_handler.write(manifest)
        pssh = await getPSSHs()
        global keys
        keys = await getKeyss(pssh=pssh, license=lic)
        if keys is not None:
            await message1.edit_text(f'''
<b>Extracted Keys:</b>

<code>--key {keys}</code>        
        ''', parse_mode='HTML')
        else:
            return msg.edit_text('<b>Still that type is Not Supported</b>')
        sleep(0.75)
        vid, aud = await (getButtons(msg))
        await message1.edit_text('''<b>
Chose video quality for download:
        </b>''', parse_mode='HTML', reply_markup=vid)

    else:
        await msg.reply_html('<b>Syntax error! use /help</b>', quote=True)
        return

app.add_handler(CommandHandler("start", start))
app.add_handler((CommandHandler("help", help)))
app.add_handler(MessageHandler(filters.ChatType.PRIVATE, input))
app.add_handler(CallbackQueryHandler(calls))


app.run_polling()
