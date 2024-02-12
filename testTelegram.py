import logging
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
) #Es para crear logs, asi comunica que hace por si hay un error

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text="Soy un bot, beep boop"
	) #Esto se ejecuta cada vez que se mande un /start

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=update.message.text
	) #Esto se ejecuta cada vez que se mande un mensaje, repetiendo lo que dice el usuario

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
	text_caps = ' '.join(context.args).upper()
	await context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=text_caps
	)

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(
		chat_id=update.effective_chat.id, 
		text=datetime.datetime.now()
	)

async def scheduleTest(update: Update, context: CallbackContext):
	

if __name__ == '__main__':
	app = ApplicationBuilder().token("1640356978:AAEYCdXn-qgIV8vPh6aK1GsZWQnF-GeylGc").build()

	start_handler = CommandHandler('start',start) #escucha al comando /start
	caps_handler = CommandHandler('caps',caps)
	echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
	time_handler = CommandHandler('time',time)
	app.add_handler(start_handler)
	app.add_handler(caps_handler)
	app.add_handler(time_handler)
	app.add_handler(echo_handler)

	app.run_polling() #mantiene al bot andando hasta que se presione CTRL+C