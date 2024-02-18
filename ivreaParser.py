import feedparser
import re
import itertools
import convertToMsg

url = "https://www.ivreality.com.ar/feed/"
feed = feedparser.parse(url)

def stripHTML(text):
	returnText = re.sub(r"<br(.*?)>",' ',text)
	returnText = re.sub(r'<.+?>', '', returnText)
	return returnText

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
			title = stripHTML(title)
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
	for x in range(len(lanzamientos)):
		lanzamientos[x] = stripHTML(lanzamientos[x])
	reediciones = re.findall(r'>(.*?)</h3>', body[1])
	for x in range(len(reediciones)):
		reediciones[x] = stripHTML(reediciones[x])
	return [lanzamientos,reediciones]

def parseLanzamiento(body):
	parrafos = re.findall(r'<p>(.*?)</p>', body)
	bulletpoints = parrafos[0].split("<br />")
	for x in range(len(bulletpoints)):
		bulletpoints[x] = stripHTML(bulletpoints[x])
	bulletpoints = list(filter(None, bulletpoints))
	return bulletpoints

def parseOtro(body):
	contenido = body.replace("\n", "")
	contenido = contenido.replace("<br />", "\n")
	contenido = re.sub(r'<.+?>', '', contenido)

	return contenido

def parseResumenAnuncios(body):
	anuncios = []
	parrafos = re.findall(r'<p>(.*?)</p>', body)
	for parrafo in parrafos:
		anuncios.append(re.findall(r'<strong>(.*?)</strong>', parrafo))
	anuncios = list(filter(None, anuncios))
	for x in range(len(anuncios)):
		for i in range(len(anuncios[x])):
			anuncios[x][i] = anuncios[x][i].split("&#8211;")
			anuncios[x][i] = list(filter(None, anuncios[x][i]))
		anuncios[x] = list(itertools.chain.from_iterable(anuncios[x]))
	return anuncios

def fetchImage(text):
	imageURL = re.findall(r'src=\"(.*?)\"', text)
	if imageURL != []:
		imageURL = imageURL[0]
	else:
		imageURL = -1
	return imageURL

def deleteReedicionesFromGroupImgs(list, start):
	trimmedList = list[:start]
	return trimmedList

#Devuelve un array con todas las imgs de los mangas que salieron hoy
def fetchGroupImgs(article):
	imgs = re.findall(r'src=\"(.*?)\"', article)
	return imgs

#Para darle formato a las novedades, vamos a poner el titulo, link, y cada manga que sale en una lista
def formatNovedades(entry):
	tipo = "Photo"
	titulo = entry.title
	link = entry.link
	imagen = fetchImage(entry.content[0]['value'])
	contenido = parseTitlesNovedades(entry.content[0]['value'])
	listaFinal = [tipo,titulo,link,imagen,contenido]
	return listaFinal

def formatSalioHoy(entry):
	tipo = "GroupPhoto"
	titulo = entry.title
	link = entry.link
	contenido = parseTitlesSalioHoy(entry.content[0]['value'])
	imagenes = deleteReedicionesFromGroupImgs(fetchGroupImgs(entry.content[0]['value']),len(contenido[0]))
	listaFinal = [tipo,titulo,link,imagenes,contenido]
	return listaFinal

def formatLanzamiento(entry):
	tipo = "Photo"
	titulo = entry.title
	link = entry.link
	imagen = fetchImage(entry.content[0]['value'])
	contenido = parseLanzamiento(entry.content[0]['value'])
	listaFinal = [tipo, titulo, link, imagen, contenido]
	return listaFinal

def formatResumenAnuncios(entry):
	tipo = "GroupPhoto"
	titulo = entry.title
	link = entry.link
	contenido = parseResumenAnuncios(entry.content[0]['value'])
	imagenes = fetchGroupImgs(entry.content[0]['value'])
	if len(imagenes)<len(contenido):
		contenido = contenido[:len(imagenes)]
	listaFinal = [tipo, titulo, link, imagenes, contenido]
	return listaFinal

def formatOtro(entry):
	tipo = "PhotoOrImage"
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
	elif "resumen de" in titulo.casefold():
		return "Resumen"
	else:
		return "Otro"

def parseArticle(entry):
	articleType = checkTypeArticle(entry.title)
	match articleType:
		case "Novedades":
			articulo = formatNovedades(entry)
			msg = convertToMsg.msgNovedades(articulo[1],articulo[2],articulo[4])
		case "SalioHoy":
			articulo = formatSalioHoy(entry)
			msg = convertToMsg.msgSalioHoy(articulo[1],articulo[2],articulo[4])
		case "Lanzamiento":
			articulo = formatLanzamiento(entry)
			msg = convertToMsg.msgLanzamiento(articulo[1],articulo[2],articulo[4])
		case "Resumen":
			articulo = formatResumenAnuncios(entry)
			msg = convertToMsg.msgResumen(articulo[1],articulo[2],articulo[4])
		case "Otro":
			articulo = formatOtro(entry)
			msg = convertToMsg.msgOtro(articulo[1],articulo[2],articulo[4])
	articulo.append(msg)
	return articulo
