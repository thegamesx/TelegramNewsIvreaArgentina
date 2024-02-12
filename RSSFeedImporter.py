import feedparser

url = "https://www.ivreality.com.ar/feed/"
feed = feedparser.parse(url)

def loadFeed():
    listOfArticles = feed.entries
    return listOfArticles

def getArticlesTitles(articles):
    titleList = []
    for entry in articles:
        titleList.append(entry.title)
    return titleList

def loadArticleFromTitle(title,articles):
    loadArticle = -1
    for x in articles:
        if title==x.title:
            loadArticle = x
    return  loadArticle
def saveEntries(listToSave):
    file = open("entries.txt","w")
    for article in listToSave:
        file.write(article + "\n")
    file.close()

#Carga el archivo y devuelve cada linea en una lista
def loadFile():
    file = open("entries.txt","r")
    lines = file.readlines()
    for x in range(len(lines)):
        lines[x] = lines[x].replace("\n","")
    file.close()
    return lines


# Esta funcion existe para eliminar un articulo del archivo en caso de fallar el envio
def deleteEntryFromFile(entryTitle):
    file = loadFile()
    for x in range(len(file)):
        if entryTitle in file[x]:
            file.pop(x)
            saveEntries(file)
            return 0
    return -1

#Este es la función principal, la cual va a devolver nuevas entradas (si las hay) para procesarlas luego
def checkForNewTitleEntries():
    articles = loadFeed()
    currentEntries = getArticlesTitles(articles)
    savedEntries = loadFile()
    newTitleEntries = []
    newEntryList = []
    for article in currentEntries:
        if not article in savedEntries:
            newTitleEntries.append(article)
    for entry in newTitleEntries:
        newEntryList.append(loadArticleFromTitle(entry,articles))
    if newEntryList != []:
        saveEntries(currentEntries)
        return reversed(newEntryList)
    else:
        return False
