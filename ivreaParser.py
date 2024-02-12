import feedparser
import re

url = "https://www.ivreality.com.ar/feed/"
feed = feedparser.parse(url)

#En los articulos que muestran que salió hoy, rescatamos los titulos en forma de lista, con sus respectivos subtitulos
def parseTitlesNovedades(body):
	titleList = []
	parsedBody = re.findall(r'<li>(.*?)</li>', body)
	if parsedBody == []:
		parsedBody = re.findall(r'<p>(.*?)</p>', body)
	for x in range(len(parsedBody)):
		title = re.findall(r'<strong>(.*?)</strong>', parsedBody[x])
		if title != []:
			if type(title) is list:
				title = title[0]
			title = re.sub(r'<.+?>','',title)
			title = title.replace("&#8221;", "\"")
			if title[0]=="•":
				title = title[2:]
			titleList.append(title)
		"""
		for x in range(len(parsedBody)):
			removeList = []
			removeFirst = 99
			title = re.findall(r'<strong>(.*?)</strong>',parsedBody[x])
			if type(title) is list:
				title = title[0]
			title = re.sub(r'<.+?>','',title)
			subtitles = parsedBody[x].split("<br />")
			subtitles.pop(0)
			#Ver si este pedazo de codigo no elimina cosas que no corresponden, probar con diferentes entradas
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
		"""
	return titleList

#Para recuperar los titulos que salieron hoy, solo vamos a concentrarnos en los titulos. (considerar los subs)
def parseTitlesSalioHoy(body):
	body = body.split("REEDICIONES")
	lanzamientos = re.findall(r'>(.*?)</h3>', body[0])
	reediciones = re.findall(r'>(.*?)</h3>', body[1])
	return [lanzamientos,reediciones]

def parseLanzamiento(body):
	parrafos = re.findall(r'<p>(.*?)</p>', body)
	bulletpoints = parrafos[0].split("<br />")
	for x in range(len(bulletpoints)):
		bulletpoints[x] = re.sub(r'<.+?>','',bulletpoints[x])
	while bulletpoints[0]=='':
		bulletpoints.pop(0)
	parrafos.pop(0)
	for x in range(len(parrafos)):
		parrafos[x] = re.sub(r'<.+?>', '', parrafos[x])
		parrafos[x] = re.sub(r'&#.+?;', '', parrafos[x])
	return [bulletpoints,parrafos]

def parseOtro(body):
	contenido = body.replace("\n", "")
	contenido = contenido.replace("<br />", "\n")
	contenido = re.sub(r'<.+?>', '', contenido)

	return contenido

def fetchImage(text):
	imageURL = re.findall(r'src=\"(.*?)\"', text)
	if imageURL != []:
		imageURL = imageURL[0]
	else:
		imageURL = -1
	return imageURL

#Devuelve un array con todas las imgs de los mangas que salieron hoy
def fetchGroupImgs(article):
	imgs = re.findall(r'src=\"(.*?)\"', article)
	return imgs

#Para darle formato a las novedades, vamos a poner el titulo, link, y cada manga que sale en una lista
def formatNovedades(entry):
	tipo = "Novedades"
	titulo = entry.title
	link = entry.link
	imagen = fetchImage(entry.content[0]['value'])
	contenido = parseTitlesNovedades(entry.content[0]['value'])
	listaFinal = [tipo,titulo,link,imagen,contenido]
	return listaFinal

def formatSalioHoy(entry):
	tipo = "SalioHoy"
	titulo = entry.title
	link = entry.link
	imagenes = fetchGroupImgs(entry.content[0]['value'])
	contenido = parseTitlesSalioHoy(entry.content[0]['value'])
	listaFinal = [tipo,titulo,link,imagenes,contenido]
	return listaFinal

def formatLanzamiento(entry):
	tipo = "Lanzamiento"
	titulo = entry.title
	link = entry.link
	imagen = fetchImage(entry.content[0]['value'])
	contenido = parseLanzamiento(entry.content[0]['value'])
	listaFinal = [tipo, titulo, link, imagen, contenido]
	return listaFinal

def formatOtro(entry):
	tipo = "Otro"
	titulo = entry.title
	link = entry.link
	imagen = fetchImage(entry.content[0]['value'])
	resumen = entry.summary
	resumen = re.sub(r'\[.+?]', '', resumen)
	if resumen == '':
		resumen = parseOtro(entry.content[0]['value'])
	listaFinal = [tipo, titulo, link, imagen, resumen]
	return listaFinal

def checkTypeArticle(titulo):
	if "novedades del" in titulo.casefold():
		return "Novedades"
	elif "todo lo que salió" in titulo.casefold():
		return "SalioHoy"
	elif "ivrea publicará" in titulo.casefold():
		return "Lanzamiento"
	else:
		return "Otro"

def parseArticle(entry):
	articleType = checkTypeArticle(entry.title)
	if articleType == "Novedades":
		articulo = formatNovedades(entry)
	if articleType == "SalioHoy":
		articulo = formatSalioHoy(entry)
	if articleType == "Lanzamiento":
		articulo = formatLanzamiento(entry)
	if articleType == "Otro":
		articulo = formatOtro(entry)

	return articulo