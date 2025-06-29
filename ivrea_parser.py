import logging
import re
import convert_to_msg as convertMsg
import requests
import math
import json


# Cargo la configuración a través de un archivo
with open('conf.json', 'r') as jsonFile:
    conf = json.load(jsonFile)
numberOfReprints = conf['numberOfReprints']


def stripHTML(text):
    returnText = re.sub(r"<br(.*?)>", ' ', text)
    returnText = re.sub(r'<.+?>', '', returnText)
    returnText = returnText.replace("&nbsp;", " ")
    return returnText.strip()


# Intentamos conseguir un link a Anilist y MAL para adjuntar al mensaje de una novedad.
def fetchDatabaseLinks(titleData):
    query = """
        query ($title: String) {
            Media (search: $title, type: MANGA) {
                id
                idMal
            }
        }
    """

    searchQuery = {
        "title": titleData[1]
        if not (titleData[1][:3].casefold() == "de " or "escrita por" in titleData[1].casefold())
        else titleData[0]
    }

    # Si el título incluye -EDICIÓN KANZENBAN- se lo sacamos
    if "-EDICIÓN KANZENBAN-" in searchQuery["title"]:
        searchQuery["title"] = searchQuery["title"].strip("-EDICIÓN KANZENBAN-")

    url = 'https://graphql.anilist.co'

    response = requests.post(url, json={'query': query, 'variables': searchQuery})

    if response.status_code == 200:
        data = response.json()
        links = {
            "anilist": data["data"]["Media"]["id"],
            "MAL": data["data"]["Media"]["idMal"]
        }
    else:
        logging.exception("Fallo la API de Anilist, con el código " + str(response.status_code) + ": " + response.reason)
        links = {
            "anilist": None,
            "MAL": None
        }

    return links


# En los artículos que muestran que salió hoy, rescatamos los títulos en forma de lista, con sus respectivos subtítulos
def parseTitlesNovedades(body):
    titleList = []
    parsedBody = re.findall(r'<li>(.*?)</li>', body)
    if not parsedBody:
        parsedBody = re.findall(r'<p>(.*?)</p>', body)
    for x in range(len(parsedBody)):
        title = re.findall(r'<strong>(.*?)</strong>', parsedBody[x])
        if title:
            if type(title) is list:
                title = title[0]
            title = stripHTML(title)
            title = title.replace("&#8221;", "\"")
            if title[0] == "•":
                title = title[2:]
            titleList.append(title)
    return titleList


# Para recuperar los títulos que salieron hoy, solo vamos a concentrarnos en los títulos. (considerar los subs)
def parseTitlesSalioHoy(body):
    problema_impresion = []
    split_body = body.split("REEDICIONES")

    lanzamientos = re.findall(r'<h\d.class="wp-block-heading">(.*?)</h\d>', split_body[0])
    for item in range(len(lanzamientos)):
        lanzamientos[item] = stripHTML(lanzamientos[item])

    reediciones = None
    if len(split_body) > 1:
        reediciones = re.findall(r'<h\d.class="wp-block-heading">(.*?)</h\d>', split_body[1])
        for item in range(len(reediciones)):
            reediciones[item] = stripHTML(reediciones[item])

    # Acá revisamos si hubo algún problema de impresión. En caso de haber más de uno se tendría que reimplementar
    # esto Como los nombres de los mangas están escritos en mayúsculas, no debería detecto eso si un manga tiene
    # imprenta en su nombre
    if "imprenta" in body:
        problem = re.findall(r'>(.*?)</h\d>', body)[-1]
        problema_impresion.append(stripHTML(problem))
        # Sacamos el último item, si fue detectado como un manga
        if "imprenta" in reediciones[-1]:
            reediciones.pop()
    return [lanzamientos, reediciones, problema_impresion]


def parseLanzamiento(body):
    parrafos = re.findall(r'<p>(.*?)</p>', body)
    bulletpoints = parrafos[0].split("<br />")
    for x in range(len(bulletpoints)):
        bulletpoints[x] = stripHTML(bulletpoints[x])
    # Nos fijamos si un item tiene demasiado texto o si está vacío, para eliminarlo de la lista
    bulletpoints = list(filter(lambda y: 150 > len(y) > 1, bulletpoints))
    return bulletpoints


# Tomamos el primer parrafo del texto.
def parseOtro(body):
    # Primero sacamos la imagen del articulo.
    contenido = re.sub(r"<figure(.*?)</figure>", '', body)
    # Luego buscamos la primera instancia de un texto encapsulado en un etiquetado de HTML
    contenido = re.findall(r'>(.*?)</[^<]+(?=>)', contenido)[0]
    contenido = stripHTML(contenido)

    return contenido


def parseResumenAnuncios(body):
    # 10/11/24: Se volvió a cambiar el formato. Esperemos que sea consistente, si no voy a discontinuar esta función
    # y hacer algo más genérico.
    # 4/4/25: El formato cambió ligeramente. Todavía estoy considerando si cambiarlo, pero por ahora solo fue acomodar
    # un par de cosas chicas.
    # 6/6/25 Se cambió una pequeña cosa, por ahora lo mantengo.
    anuncios = []
    items = re.findall(r'<p>(.*?)</p>', body)
    if len(items) <= 4:
        items = re.findall(r'<li>(.*?)</li>', body)
        for item in items:
            lineaItem = []
            titulo = re.search(r'<a(.*?)</a>', item)
            if not titulo:
                titulo = re.search(r'<strong(.*?)</strong>', item).group()
                link = None
            else:
                titulo = re.search(r'<a(.*?)</a>', item).group()
                link = [re.search(r'href="(.*?)">', titulo).group()[5:-1]][0]
            titulo = stripHTML(titulo)
            if titulo[-1] == ":":
                titulo = titulo[:-1]
            bulletpoints = re.sub(r"<a(.*?)</a>", '', item).split("&#8211;")
            bulletpoints[0] = re.sub(r"<strong(.*?)</strong>", '', bulletpoints[0])
            bulletpoints[0] = re.sub(r"<a(.*?)</a>", '', bulletpoints[0])
            lineaItem.append(link)
            lineaItem.append(titulo)
            for line in bulletpoints:
                lineaItem.append(stripHTML(line))
            anuncios.append(lineaItem)
    else:
        for item in items:
            lineaItem = [re.search(r'href="(.*?)/">', item).group()[5:-1]]
            bulletpoints = item.split("&#8211;")[1:]
            bulletpoints.insert(1, bulletpoints[0].split("</strong>")[1])
            bulletpoints[0] = bulletpoints[0].split("<")[0][:-1]
            for line in bulletpoints:
                lineaItem.append(stripHTML(line))
            anuncios.append(lineaItem)
    return anuncios


def fetchImage(text):
    imageURL = re.findall(r'src=\"(.*?)\"', text)
    if imageURL:
        imageURL = imageURL[0]
    else:
        imageURL = -1
    return imageURL


# Ver si es necesario mantener esta funcion, es muy simple
def deleteReedicionesFromGroupImgs(lista, start):
    return lista[:start]


# Devuelve un array con todas las imgs de los mangas que salieron hoy
def fetchGroupImgs(article):
    imgs = re.findall(r'src=\"(.*?)\"', article)
    # Filtramos por imagenes que esten en el dominio de ivreality, así evitamos emojis
    return [url for url in imgs if 'ivreality.com.ar' in url]


# Para darle formato a las novedades, vamos a poner el título, link, y cada manga que sale en una lista
def formatNovedades(entry):
    tipo = "Photo"
    titulo = entry.title
    link = entry.link
    contenido = parseTitlesNovedades(entry.content[0]['value'])
    imagen = fetchGroupImgs(entry.content[0]['value'])
    # Puede que hayan multiples imágenes. En ese caso vemos si son más de una (ignorando reediciones) y categorizamos
    # el post según corresponda
    reediciones = 0
    for item in contenido:
        if "(reedición)" in item.casefold() or "(reediciones)" in item.casefold():
            reediciones += 1
    if len(imagen) > 1 and reediciones > 0:
        imagen = imagen[:-int(math.ceil(reediciones/numberOfReprints))]
    if len(imagen) == 1:
        imagen = imagen[0]
    else:
        tipo = "GroupPhoto"
    listaFinal = {
        "tipo": tipo,
        "titulo": titulo,
        "link": link,
        "media": imagen,
        "contenido": contenido
    }
    return listaFinal


def formatSalioHoy(entry):
    tipo = "GroupPhoto"
    titulo = entry.title
    link = entry.link
    contenido = parseTitlesSalioHoy(entry.content[0]['value'])
    imagenes = deleteReedicionesFromGroupImgs(fetchGroupImgs(entry.content[0]['value']), len(contenido[0]))
    listaFinal = {
        "tipo": tipo,
        "titulo": titulo,
        "link": link,
        "media": imagenes,
        "contenido": contenido
    }
    return listaFinal


def formatLanzamiento(entry):
    tipo = "Photo"
    titulo = entry.title
    link = entry.link
    imagen = fetchImage(entry.content[0]['value'])
    contenido = parseLanzamiento(entry.content[0]['value'])
    linksExternos = fetchDatabaseLinks(contenido)
    listaFinal = {
        "tipo": tipo,
        "titulo": titulo,
        "link": link,
        "media": imagen,
        "contenido": contenido,
        "databaseLinks": linksExternos
    }
    return listaFinal


def formatResumenAnuncios(entry):
    tipo = "GroupPhoto"  # Lo declaramos acá por las dudas
    titulo = entry.title
    link = entry.link
    contenido = parseResumenAnuncios(entry.content[0]['value'])
    imagenes = fetchGroupImgs(entry.content[0]['value'])
    if len(imagenes) == 1:
        tipo = "Photo"
        imagenes = imagenes[0]
    listaFinal = {
        "tipo": tipo,
        "titulo": titulo,
        "link": link,
        "media": imagenes,
        "contenido": contenido
    }
    return listaFinal


def formatOtro(entry):
    tipo = "PhotoOrText"
    titulo = entry.title
    link = entry.link
    imagen = fetchImage(entry.content[0]['value'])
    resumen = parseOtro(entry.content[0]['value'])
    listaFinal = {
        "tipo": tipo,
        "titulo": titulo,
        "link": link,
        "media": imagen,
        "contenido": resumen
    }
    return listaFinal


def checkTypeArticle(articulo):
    if "novedades del" in articulo.title.casefold():
        return "Novedades"
    elif "todo lo que sali" in articulo.title.casefold():
        return "SalioHoy"
    elif "resumen de" in articulo.title.casefold():
        return "Resumen"
    elif articulo.content[0]['value'].count("<br />") > 2:
        return "Lanzamiento"
    else:
        return "Otro"


def parseArticle(entry):
    articleType = checkTypeArticle(entry)
    match articleType:
        case "Novedades":
            articulo = formatNovedades(entry)
            msg = convertMsg.msgNovedades(articulo["titulo"], articulo["link"], articulo["contenido"])
        case "SalioHoy":
            articulo = formatSalioHoy(entry)
            msg = convertMsg.msgSalioHoy(articulo["titulo"], articulo["link"], articulo["contenido"])
        case "Lanzamiento":
            articulo = formatLanzamiento(entry)
            msg = convertMsg.msgLanzamiento(articulo["titulo"], articulo["link"], articulo["contenido"],
                                            articulo["databaseLinks"])
        case "Resumen":
            articulo = formatResumenAnuncios(entry)
            msg = convertMsg.msgResumen(articulo["titulo"], articulo["link"], articulo["contenido"])
        case "Otro":
            articulo = formatOtro(entry)
            msg = convertMsg.msgOtro(articulo["titulo"], articulo["link"], articulo["contenido"])
    articulo["mensaje"] = msg
    return articulo
