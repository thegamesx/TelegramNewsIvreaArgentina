import time
from RSSFeedImporter import checkForNewEntries, deleteEntryFromFile
from telegramSend import sendPost
from ivreaParser import parseArticle
import schedule
import logging
import json

# Crea un archivo para el logging
logging.basicConfig(filename="logging.log", encoding="utf-8", level=logging.DEBUG)

# Cargo la configuración a través de un archivo
with open('conf.json', 'r') as jsonFile:
    conf = json.load(jsonFile)
intervalHours = conf['intervalHours']


# Revisa si hay artículos nuevos. Si los hay los manda, y chequea que funcione correctamente
def checkForNewAndSend():
    newPosts = checkForNewEntries()
    if newPosts:
        for article in newPosts:
            try:
                articleToSend = parseArticle(article)
                sendPost(articleToSend[0], articleToSend[5], articleToSend[3])
                logging.info("Se envió " + article.title)
            except Exception as error:
                logging.error("Falló el envió de " + article.title + " El error fue el siguiente:\n", error)
                if deleteEntryFromFile(article.title):
                    logging.info(
                        "Se eliminó " + article.title + " del registro. Se volverá a intentar en el próximo schedule")
                else:
                    logging.error("No se eliminó " + article.title + "del registro. Revisar manualmente.")
    else:
        logging.info("Se ejecutó el programa. No hay nuevos artículos.")


schedule.every(intervalHours).hours.do(checkForNewAndSend)

if __name__ == "__main__":
    # Ejecutamos el query al arrancar el programa, y luego lo hacemos cada x hs
    checkForNewAndSend()
    while True:
        schedule.run_pending()
        time.sleep(1)

# TODO: Emprolijar el guardado de articulos enviados. Que solo lo guarde si fue exitoso
