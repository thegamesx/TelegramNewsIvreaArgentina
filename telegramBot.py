import telegram
import asyncio

async def main():
	bot = telegram.Bot("1640356978:AAEYCdXn-qgIV8vPh6aK1GsZWQnF-GeylGc")
	async with bot:
		await bot.send_message(text='Que hace perro', chat_id=924728423)

if __name__ == '__main__':
	asyncio.run(main())

