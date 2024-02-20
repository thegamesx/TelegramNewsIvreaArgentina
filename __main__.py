import time
from RSSFeedImporter import checkForNewEntries,deleteEntryFromFile,loadFeed
from telegramSend import sendPost
from ivreaParser import parseArticle
import schedule
import logging
import json

#Crea un archivo para el logging
logging.basicConfig(filename="logging.log", encoding="utf-8",level=logging.DEBUG)

# Cargo la configuracion a traves de un archivo
with open('conf.json','r') as jsonFile:
	conf = json.load(jsonFile)
intervalHours = conf['intervalHours']

def checkForNewAndSend():
    newPosts = checkForNewEntries()
    if newPosts:
        for article in newPosts:
            try:
                articleToSend = parseArticle(article)
                sendPost(articleToSend[0],articleToSend[5],articleToSend[3])
                logging.info("Se envió " + article.title)
            except Exception as error:
                logging.error("Falló el envió de " + article.title + " El error fue el siguiente:\n",error)
                if deleteEntryFromFile(article.title):
                    logging.info("Se eliminó " + article.title + " del registro. Se volverá a intentar en el próximo schedule")
                else:
                    logging.error("No se eliminó " + article.title + "del registro. Revisar manualmente.")
    else:
        logging.info("Se ejecutó el programa. No hay nuevos articulos.")

schedule.every(intervalHours).hours.do(checkForNewAndSend)

def test(articleNumber):
    feed = loadFeed()
    articleToSend = parseArticle(feed[articleNumber])
    sendPost(articleToSend[0],articleToSend[5],articleToSend[3])

if __name__ == "__main__":
    #Ejecutamos el query al arrancar el programa, y luego lo hacemos cada x hs
    checkForNewAndSend()
    while True:
        schedule.run_pending()
        time.sleep(1)
