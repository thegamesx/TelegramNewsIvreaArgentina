import time
from RSSFeedImporter import checkForNewEntries, saveEntries
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
    errors = []
    if newPosts:
        for index, article in enumerate(newPosts):
            articleLinks = "\nLink: " + article.link + "\nID: " + article.id
            try:
                articleToSend = parseArticle(article)
                sendPost(articleToSend["tipo"], articleToSend["mensaje"], articleToSend["media"])
                logging.info("Se envió " + article.title + articleLinks)
            except Exception as error:
                msgError = ("Falló el envió de " + article.title + " El error fue el siguiente:\n" + repr(error) +
                            articleLinks)
                logging.error(msg=msgError)
                # Mandar mensaje a un canal alternativo informando el error
                sendPost("PhotoOrText", msgError, -1, True)
                # Guardo el índice del artículo en el que hubo un error, asi puedo sacarlo de la lista luego del for.
                errors.append(index)
        if errors:
            # Elimino de la lista los artículos que no se enviaron
            newPosts[:] = [entry for index, entry in enumerate(newPosts) if index not in errors]
        saveEntries(newPosts)
    else:
        logging.info("No hay nuevos artículos.")


schedule.every(intervalHours).hours.do(checkForNewAndSend)

if __name__ == "__main__":
    # Ejecutamos el query al arrancar el programa, y luego lo hacemos cada x hs
    checkForNewAndSend()
    while True:
        schedule.run_pending()
        time.sleep(1)
