import feedparser
import re
from datetime import datetime, timedelta

url = "https://www.ivreality.com.ar/feed/"
feed = feedparser.parse(url)

#En los articulos que muestran que salió hoy, rescatamos los titulos en forma de lista
def parseTitles(body):
	result = []
	parsedBody = re.findall(r'<li>(.*?)</li>', body)
	for x in range(len(parsedBody)):
		removeList = []
		removeFirst = 99
		title = re.findall(r'<strong>(.*?)</strong>',parsedBody[x])
		if type(title) is list:
			title = title[0]
		title = re.sub(r'<.+?>','',title)
		subtitles = parsedBody[x].split("<br />")
		subtitles.pop(0)
		for x in range(len(subtitles)):
			subtitles[x] = re.sub(r'<.+?>','',subtitles[x])
			if subtitles[x][:1]=='–':
				subtitles[x] = subtitles[x][2:]
			if not subtitles[x] and removeFirst==99:
				removeFirst = x
		for x in range(len(subtitles)):
			if x>=removeFirst and x<=len(subtitles)-1:
				removeList.append(x)
		#Revierto el orden de la lista para evitar errores de out of index
		if removeList!=[]:
			for x in reversed(removeList): 
				subtitles.pop(x)

		subtitles.insert(0,title)
		result.append(subtitles)

	return result


def getLastEntry():
	entry = feed.entries[0]
	body = entry.title + '\n' + '\n' + entry.content
	return (entry.title)

def fetchNovedadesImage(text):
	imageURL = re.findall(r'src=\"(.*?)\"', text)
	imageURL = imageURL[0]
	return imageURL

#Para darle formato a las novedades, vamos a poner el titulo, link, y cada manga que sale en una lista
def formatNovedades(entry):
	titulo = entry.title
	link = entry.link
	imagen = fetchNovedadesImage(entry.content[0]['value'])
	contenido = parseTitles(entry.content[0]['value'])
	listaFinal = [titulo,link,imagen,contenido]

	return listaFinal

def formatSalioHoy(entry):
	titulo = entry.title
	link = entry.link
	contenido = parseTitles(entry.content[0]['value'])
	listaFinal = [titulo,link,contenido]

	return listaFinal

def formatOtro(entry):
	pass

def checkTypeArticle(titulo):
	if "Novedades del" in titulo:
		return "Novedades"
	elif "Todo lo que salió" in titulo:
		return "SalioHoy"
	else:
		return "Otro"

def parseArticle(entry):
	articleType = checkTypeArticle(entry.title)
	if articleType == "Novedades":
		articulo = formatNovedades(entry)
	if articleType == "SalioHoy":
		articulo = formatSalioHoy(entry)
	if articleType == "Otro":
		articulo = formatOtro(entry)

	return articulo

def checkForLastEntry():
	feed = feedparser.parse(url)
	return feed.entries[0]
	#Poner un codigo para que no vuelva a mandar algo que ya se mandó

article = checkForLastEntry()
if article != 0:
	mensaje = parseArticle(article)
print (mensaje)