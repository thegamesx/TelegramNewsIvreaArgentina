import time
from RSSFeedImporter import checkForNewTitleEntries,deleteEntryFromFile
from telegramSend import sendPost
from ivreaParser import parseArticle
import schedule
import logging

#Crea un archivo para el logging
logging.basicConfig(filename="logging.log", encoding="utf-8",level=logging.DEBUG)

def checkForNewAndSend():
    newPosts = checkForNewTitleEntries()
    if newPosts:
        for article in newPosts:
            try:
                sendPost(parseArticle(article))
                logging.info("Se envió " + article.title)
            except:
                logging.error("Falló el envió de " + article.title)
                if deleteEntryFromFile(article.title)==0:
                    logging.info("Se eliminó " + article.title + " del registro. Se volverá a intentar en el próximo schedule")
                else:
                    logging.error("No se eliminó " + article.title + "del registro. Revisar manualmente.")
    else:
        logging.info("Se ejecutó el programa. No hay nuevos articulos.")

schedule.every(3).hours.do(checkForNewAndSend)

if __name__ == "__main__":
    #Ejecutamos el query al arrancar el programa, y luego lo hacemos cada 3hs
    checkForNewAndSend()
    while True:
        schedule.run_pending()
        time.sleep(1)
