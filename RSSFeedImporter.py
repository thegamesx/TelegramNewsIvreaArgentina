import feedparser
import os.path

url = "https://www.ivreality.com.ar/feed/"


# Actualiza el feed para ver si hay artículos nuevos
def loadFeed():
    feed = feedparser.parse(url)
    listOfArticles = feed.entries
    return listOfArticles


def getArticlesID(articles):
    IDList = []
    for entry in articles:
        IDList.append(entry.id)
    return IDList


def loadArticleFromID(ID, articles):
    loadArticle = -1
    for x in articles:
        if ID == x.id:
            loadArticle = x
    return loadArticle


# Guarda un archivo con los artículos que se enviaron
def saveEntries(listToSave):
    file = open("entries.txt", "w")
    for article in listToSave:
        file.write(article + "\n")
    file.close()


# Carga el archivo y devuelve cada linea en una lista
def loadFile():
    if os.path.isfile("./entries.txt"):
        file = open("entries.txt", "r")
        lines = file.readlines()
        for x in range(len(lines)):
            lines[x] = lines[x].replace("\n", "")
        file.close()
        return lines
    else:
        saveEntries([])
        return []


# Esta función existe para eliminar un articulo del archivo en caso de fallar el envio
def deleteEntryFromFile(entryTitle):
    file = loadFile()
    for x in range(len(file)):
        if entryTitle in file[x]:
            file.pop(x)
            saveEntries(file)
            return True
    return False


# Este es la función principal, la cual va a devolver nuevas entradas (si las hay) para procesarlas luego
def checkForNewEntries():
    articles = loadFeed()
    currentEntries = getArticlesID(articles)
    savedEntries = loadFile()
    newEntries = []
    newEntryList = []
    for article in currentEntries:
        if not article in savedEntries:
            newEntries.append(article)
    for entry in newEntries:
        newEntryList.append(loadArticleFromID(entry, articles))
    if newEntryList:
        saveEntries(currentEntries)
        return reversed(newEntryList)
    else:
        return False
