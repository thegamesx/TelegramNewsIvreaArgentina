import ivreaParser
import convertToMsg
import json
import asyncio
import logging
import telegram
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder

# Cargo las credenciales a traves de un archivo
with open('credentials.json','r') as jsonFile:
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


# Arregla los links para poder enviarlos como grupo
def prepareMedia(list):
	correctList = []
	for img in list:
		correctList.append(telegram.InputMediaPhoto(media=img))
	return correctList

#Envia un articulo que no sea reconocido. En este caso vemos si tiene una img. En ese caso se manda con una caption. En caso contrario se manda un mensaje
async def sendOtro(app, chat, msg, img):
	if img == -1:
		await app.bot.sendMessage(
			chat_id=chat,
			text=msg,
			parse_mode=ParseMode.HTML
		)
	else:
		await app.bot.sendPhoto(
			chat_id=chat,
			photo=img,
			caption=msg,
			parse_mode=ParseMode.HTML
		)


# Envia las novedades. Incluye una imagen antes de un mensaje con los proximos lanzamientos
async def sendNovedades(app, chat, msg, img):
	if len(msg) <= 1024:
		await app.bot.sendPhoto(
			chat_id=chat,
			photo=img,
			caption=msg,
			parse_mode=ParseMode.HTML
		)
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

#Envia el anuncio de una serie nueva. Se manda como una imagen con la descripcion (hay que tener cuidado que no sea mayor a 1024)
async def sendLanzamiento(app, chat, msg, img):
	await app.bot.sendPhoto(
		chat_id=chat,
		photo=img,
		caption=msg,
		parse_mode=ParseMode.HTML
	)

# Envia lo que salió hoy. Primero manda un grupo con las fotos de los mangas, y luego el detalle en un mensaje
async def sendSalioHoy(app, chat, msg, imgs):
	correctImgs = prepareMedia(imgs)
	#Mejorar esto para que funcione con mas de 20 entradas
	while len(correctImgs) > 10:
		await app.bot.sendMediaGroup(
			chat_id=chat,
			media=correctImgs[:10]
		)
		correctImgs = correctImgs[10:]
	else:
		if len(correctImgs)>1:
			await app.bot.sendMediaGroup(
				chat_id=chat,
				media=correctImgs
			)
	await app.bot.sendMessage(
		chat_id=chat,
		disable_web_page_preview=True,
		text=msg,
		parse_mode=ParseMode.HTML
	)

def initBot():
	app = ApplicationBuilder().token(myToken).read_timeout(30).write_timeout(30).build()
	return app
def sendPost(articulo):
	bot = initBot()
	match articulo[0]:
		case "Novedades":
			asyncio.run(
				sendNovedades(bot,channelID, convertToMsg.msgNovedades(articulo[1], articulo[2], articulo[4]), articulo[3]))
		case "SalioHoy":
			asyncio.run(sendSalioHoy(bot,channelID, convertToMsg.msgSalioHoy(articulo[1], articulo[2], articulo[4]), articulo[3]))
		case "Lanzamiento":
			asyncio.run(
				sendLanzamiento(bot,channelID, convertToMsg.msgLanzamiento(articulo[1], articulo[2], articulo[4][0]),
								articulo[3]))
		case "Otro":
			asyncio.run(
				sendOtro(bot,channelID, convertToMsg.msgOtro(articulo[1], articulo[2], articulo[4]), articulo[3]))