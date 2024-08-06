import json
import asyncio
import logging
from time import sleep
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
alertID = credentials['alertID']

# Es para crear logs, asi comunica que hace por si hay un error
logging.basicConfig(
    filename='logging.log',
    encoding='utf-8',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# Devuelve el tipo de archivo que tiene una url. Importante para saber si se trata de una imagen o video
def checkFiletype(mediaURL):
    req = urllib.request.Request(mediaURL, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
    r = urllib.request.urlopen(req)
    mediatype = r.getheader('Content-Type')
    return mediatype.split("/")[0]


# Borra los archivos descargados luego de mandarlos
def deleteTemp():
    for root, dirs, files in os.walk('.temp'):
        for file in files:
            if file.endswith('.jpg'):
                os.remove(os.path.join(root, file))


# En caso de que falle en mandar por un problema de tipo de archivo, vamos a descargar el archivo en vez de mandarlo
# por URL
def downloadMedia(imgURL):
    localPath = "./.temp/" + imgURL.split('/')[-1]
    # Me aseguro que exista la carpeta antes de usarla
    if not os.path.exists(".temp/"):
        os.makedirs(".temp/")
    parsedURL = "https://" + urllib.parse.quote(imgURL[8:])
    urllib.request.urlretrieve(parsedURL, localPath)
    return localPath


# Arregla los links para poder enviarlos como grupo
def prepareMedia(mediaList, message=-1, download=False):
    correctList = []
    # Aca agregamos un caption al primer elemento, ademas de acomodar las fotos. Se hace solo si recibimos un msg
    # para agregar o si el msg es muy largo
    if message == -1 or len(message) > 1024:
        for img in mediaList:
            if download:
                correctList.append(telegram.InputMediaPhoto(media=(open(downloadMedia(img), 'rb'))))
            else:
                correctList.append(telegram.InputMediaPhoto(media=img))
    else:
        if len(mediaList) > 10:
            positionForCaption = len(mediaList) - 9
        else:
            positionForCaption = 1
        for i, img in enumerate(mediaList, start=1):
            if download:
                correctList.append(telegram.InputMediaPhoto(media=(open(downloadMedia(img), 'rb')),
                                                            caption=message if i == positionForCaption else '',
                                                            parse_mode=ParseMode.HTML))
            else:
                correctList.append(
                    telegram.InputMediaPhoto(media=img, caption=message if i == positionForCaption else '',
                                             parse_mode=ParseMode.HTML))
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


# Envia un video. No debería suceder seguido, pero dejó la opción de mandar esto por las dudas.
async def sendVideo(app, chat, msg, video):
    if len(msg) <= 1024:
        try:
            await app.bot.sendVideo(
                chat_id=chat,
                video=video,
                caption=msg,
                parse_mode=ParseMode.HTML
            )
        except:
            downloadedVideo = downloadMedia(video)
            await app.bot.sendVideo(
                chat_id=chat,
                video=downloadedVideo,
                caption=msg,
                parse_mode=ParseMode.HTML
            )
            deleteTemp()
    else:
        await app.bot.sendVideo(
            chat_id=chat,
            video=video,
        )
        await app.bot.sendMessage(
            chat_id=chat,
            disable_web_page_preview=True,
            text=msg,
            parse_mode=ParseMode.HTML
        )


# Envia un artículo que no sea reconocido. En este caso vemos si tiene una img. En ese caso se manda con una caption.
# En caso contrario se manda un mensaje
async def sendMessageOrPhoto(app, chat, msg, media):
    if media == -1:
        await app.bot.sendMessage(
            chat_id=chat,
            text=msg,
            parse_mode=ParseMode.HTML
        )
    else:
        filetype = checkFiletype(media)
        if filetype == "image":
            await sendPhoto(app, chat, msg, media)
        elif filetype == "video":
            await sendVideo(app, chat, msg, media)
        else:
            logging.error(msg="No se reconoce el tipo de archivo para mandar (No es ni una foto ni un video)")


# Envia lo que salió hoy. Primero manda un grupo con las fotos de los mangas, y luego el detalle en un mensaje
async def sendGroupPhoto(app, chat, msg, imgs):
    # Vamos a defaultear a descargar las imgs, por las dudas. Cambiar esto en un futuro para que sea opcional
    correctImgs = prepareMedia(imgs, msg, download=True)
    # Envia grupos de a 10 imágenes
    while len(correctImgs) > 10:
        if len(correctImgs) % 10 != 0:
            limit = len(correctImgs) % 10
        else:
            limit = 10
        await app.bot.sendMediaGroup(
            chat_id=chat,
            media=correctImgs[:limit],
        )
        correctImgs = correctImgs[limit:]
        sleep(3)
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
def sendPost(articleType, msg, media, alternativeChannel=False):
    channel = alertID if alternativeChannel else channelID
    bot = initBot()
    match articleType:
        case "Photo":
            asyncio.run(sendPhoto(bot, channel, msg, media))
        case "GroupPhoto":
            asyncio.run(sendGroupPhoto(bot, channel, msg, media))
        case "PhotoOrText":
            asyncio.run(sendMessageOrPhoto(bot, channel, msg, media))
