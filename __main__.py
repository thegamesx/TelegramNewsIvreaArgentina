import time
from rss_importer import checkForNewEntries, saveEntries
from telegram_send import sendPost
from ivrea_parser import parseArticle
import schedule
import logging
import json

# Crea un archivo para el logging
logging.basicConfig(filename="logging.log", encoding="utf-8", level=logging.DEBUG)

# Cargo la configuración a través de un archivo
with open('conf.json', 'r') as jsonFile:
    conf = json.load(jsonFile)
intervalHours = conf['intervalHours']


def sendNewEntries(entries):
    errors = []
    for index, article in enumerate(entries):
        articleLinks = "\nLink: " + article.link + "\nID: " + article.id
        try:
            articleToSend = parseArticle(article)
            sendPost(articleToSend["tipo"], articleToSend["mensaje"], articleToSend["media"])
            logging.info("Se envió " + article.title + articleLinks)
        except Exception as error:
            msgError = ("Falló el envió de " + article.title + " El error fue el siguiente:\n" + repr(error) +
                        articleLinks)
            msgError = msgError.replace("&", "&amp;")
            msgError = msgError.replace("<", "&lt;")
            msgError = msgError.replace(">", "&gt;")
            logging.error(msg=msgError)
            # Mandar mensaje a un canal alternativo informando el error
            sendPost("PhotoOrText", msgError, -1, True)
            # Guardo el índice del artículo en el que hubo un error, asi puedo sacarlo de la lista luego del for
            errors.append(index)
    if errors:
        # Elimino de la lista los artículos que no se enviaron
        entries[:] = [entry for index, entry in enumerate(entries) if index not in errors]
    saveEntries(entries)


# Revisa si hay artículos nuevos. Si los hay los manda, y chequea que funcione correctamente
def checkForNewAndSend():
    result = checkForNewEntries()

    if not result["success"]:
        logging.error(result["error"])
    else:
        if result["data"]:
            sendNewEntries(result["data"])
        else:
            logging.info("No hay nuevos artículos.")


schedule.every(intervalHours).hours.do(checkForNewAndSend)

if __name__ == "__main__":
    # Ejecutamos el query al arrancar el programa, y luego lo hacemos cada x hs
    checkForNewAndSend()
    while True:
        schedule.run_pending()
        time.sleep(1)
