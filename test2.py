import ivreaParser

import asyncio
import logging
import datetime
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

#Despues pasar esta info a un archivo externo
myToken = "1640356978:AAEYCdXn-qgIV8vPh6aK1GsZWQnF-GeylGc"
channelID = -1002117571595

#Es para crear logs, asi comunica que hace por si hay un error
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#Envia un mensaje a traves de un comando	
async def send(chat, msg):
	await app.bot.sendMessage(
		chat_id=chat,
		text=msg,
		#parse_mode=ParseMode.MARKDOWN_V2
	)

if __name__ == '__main__':
	app = ApplicationBuilder().token(myToken).build()
	print (ivreaParser.getLastEntry())
	asyncio.run(send(channelID,ivreaParser.getLastEntry()))

	#app.run_polling() 
	#mantiene al bot andando hasta que se presione CTRL+C