import json
import asyncio
import logging
import telegram
import os
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder
import urllib.request

# Cargo las credenciales a través de un archivo
with open('credentials.json', 'r') as jsonFile:
    credentials = json.load(jsonFile)
myToken = credentials['token']
channelID = credentials['channelID']

# Es para crear logs, asi comunica que hace por si hay un error
logging.basicConfig(
    filename='logging.log',
    encoding='utf-8',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Borra los archivos descargados luego de mandarlos
def deleteTemp():
    for root, dirs, files in os.walk('./.temp'):
        for file in files:
            if file.endswith('.jpg'):
                os.remove(os.path.join(root, file))


# En caso de que falle en mandar por un problema de tipo de archivo, vamos a descargar el archivo en vez de mandarlo
# por URL
def downloadMedia(imgURL):
    name = imgURL.split('/')
    name = name[-1]
    # Me aseguro que exista la carpeta antes de usarla
    if not os.path.exists("./.temp/"):
        os.makedirs("./.temp/")
    name = "./.temp/" + name
    urllib.request.urlretrieve(imgURL, name)
    return name


# Arregla los links para poder enviarlos como grupo
def prepareMedia(mediaList, msg, download=False):
    correctList = []
    firstElement = True
    # Aca agregamos un caption al primer elemento, ademas de acomodar las fotos. Se hace solo si recibimos un msg
    # para agregar o si el msg es muy largo
    if msg == -1 or len(msg) > 1024:
        for img in mediaList:
            if download:
                correctList.append(telegram.InputMediaPhoto(media=(open(downloadMedia(img), 'rb'))))
            else:
                correctList.append(telegram.InputMediaPhoto(media=img))
    else:
        for img in mediaList:
            if download:
                correctList.append(telegram.InputMediaPhoto(media=(open(downloadMedia(img), 'rb')),
                                                            caption=msg if firstElement else '',
                                                            parse_mode=ParseMode.HTML))
            else:
                correctList.append(
                    telegram.InputMediaPhoto(media=img, caption=msg if firstElement else '', parse_mode=ParseMode.HTML))
            firstElement = False
    return correctList


# Envia una foto con un caption. Se puede usar para lanzamientos, anuncios u otros que tengan una foto.
async def sendPhoto(app, chat, msg, img):
    if len(msg) <= 1024:
        try:
            await app.bot.sendPhoto(
                chat_id=chat,
                photo=img,
                caption=msg,
                parse_mode=ParseMode.HTML
            )
        except:
            downloadedImg = downloadMedia(img)
            await app.bot.sendPhoto(
                chat_id=chat,
                photo=downloadedImg,
                caption=msg,
                parse_mode=ParseMode.HTML
            )
            deleteTemp()
    else:
        await app.bot.sendPhoto(
            chat_id=chat,
            photo=img,
        )
        await app.bot.sendMessage(
            chat_id=chat,
            disable_web_page_preview=True,
            text=msg,
            parse_mode=ParseMode.HTML
        )


# Envia un artículo que no sea reconocido. En este caso vemos si tiene una img. En ese caso se manda con una caption.
# En caso contrario se manda un mensaje
async def sendMessageOrPhoto(app, chat, msg, img):
    if img == -1:
        await app.bot.sendMessage(
            chat_id=chat,
            text=msg,
            parse_mode=ParseMode.HTML
        )
    else:
        await sendPhoto(app, chat, msg, img)


# Envia lo que salió hoy. Primero manda un grupo con las fotos de los mangas, y luego el detalle en un mensaje
async def sendGroupPhoto(app, chat, msg, imgs):
    # Vamos a defaultear a descargar las imgs, por las dudas. Cambiar esto en un futuro para que sea opcional
    correctImgs = prepareMedia(imgs, msg, download=True)
    # Envia grupos de a 10 imagenes
    while len(correctImgs) > 10:
        await app.bot.sendMediaGroup(
            chat_id=chat,
            media=correctImgs[10:],
        )
        correctImgs = correctImgs[:10]
    else:
        await app.bot.sendMediaGroup(
            chat_id=chat,
            media=correctImgs,
        )
    if len(msg) > 1024:
        await app.bot.sendMessage(
            chat_id=chat,
            disable_web_page_preview=True,
            text=msg,
            parse_mode=ParseMode.HTML
        )
    deleteTemp()


# Inicializa el bot
def initBot():
    app = ApplicationBuilder().token(myToken).read_timeout(30).write_timeout(30).build()
    return app


# Revisa que tipo de artículo es, y lo manda a la función correspondiente
def sendPost(type, msg, imgs):
    bot = initBot()
    match type:
        case "Photo":
            asyncio.run(sendPhoto(bot, channelID, msg, imgs))
        case "GroupPhoto":
            asyncio.run(sendGroupPhoto(bot, channelID, msg, imgs))
        case "PhotoOrText":
            asyncio.run(sendMessageOrPhoto(bot, channelID, msg, imgs))
