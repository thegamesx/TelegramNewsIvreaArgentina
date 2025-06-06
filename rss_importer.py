import feedparser
import os.path

url = "https://www.ivreality.com.ar/feed/"


# Revisa si el archivo está vacío
def isNonZeroFile(fpath):
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


# Actualiza el feed para ver si hay artículos nuevos
def loadFeed():
    feed = feedparser.parse(url)
    return feed.entries


def getArticlesID(articles):
    IDList = []
    for entry in articles:
        IDList.append(entry.id)
    return IDList


def loadArticleFromID(ID, articles):
    loadArticle = -1
    for entry in articles:
        if ID == entry.id:
            loadArticle = entry
    return loadArticle


# Limpia el archivo si hay más de 21 líneas
def truncateFile():
    with open('entries.txt', 'r') as fin:
        entries = fin.readlines()
    if len(entries) > 20:
        with open('entries.txt', 'w') as fout:
            fout.writelines(entries[len(entries) - 20:])


# Guarda un archivo con los artículos que se enviaron
def saveEntries(listToSave):
    listID = getArticlesID(listToSave)
    file = open("entries.txt", "a")
    for index, article in enumerate(listID):
        file.write(article if index == 0 and not isNonZeroFile("entries.txt") else "\n" + article)
    file.close()
    truncateFile()


# Carga el archivo y devuelve cada línea en una lista
def loadFile():
    if os.path.isfile("entries.txt"):
        file = open("entries.txt", "r")
        lines = file.readlines()
        for x in range(len(lines)):
            lines[x] = lines[x].replace("\n", "")
        file.close()
        return lines
    else:
        saveEntries([])
        return []


# Este es la función principal, la cual va a devolver nuevas entradas (si las hay) para procesarlas luego
def checkForNewEntries():
    articles = loadFeed()
    if not articles:
        return {"success": False, "data": None,
                "error": "El feed está vacío. La página está caída o hay un error en la conexión."}

    currentEntries = getArticlesID(articles)
    savedEntries = loadFile()

    newEntries = [entry for entry in currentEntries if entry not in savedEntries]
    newEntryList = [loadArticleFromID(entry, articles) for entry in newEntries]

    if newEntryList:
        return {"success": True, "data": newEntryList[::-1], "error": None}
    else:
        return {"success": True, "data": None, "error": None}
