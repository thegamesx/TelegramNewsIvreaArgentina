import re
import itertools
import convert_to_msg as convertMsg


def stripHTML(text):
    returnText = re.sub(r"<br(.*?)>", ' ', text)
    returnText = re.sub(r'<.+?>', '', returnText)
    returnText = returnText.replace("&nbsp;", " ")
    returnText = returnText.strip()
    return returnText


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


# Para recuperar los titulos que salieron hoy, solo vamos a concentrarnos en los titulos. (considerar los subs)
def parseTitlesSalioHoy(body):
    problemaImpresion = []
    body = body.split("REEDICIONES")
    lanzamientos = re.findall(r'>(.*?)</h\d>', body[0])
    for item in range(len(lanzamientos)):
        lanzamientos[item] = stripHTML(lanzamientos[item])
        # Si hay un aviso que un manga no se imprimió a tiempo, se agrega el aviso a una lista aparte
        if "Por problemas de imprenta" in lanzamientos[item]:
            problemaImpresion.append(lanzamientos[item])
            lanzamientos.pop()
    try:
        reediciones = re.findall(r'>(.*?)</h\d>', body[1])
        for item in range(len(reediciones)):
            reediciones[item] = stripHTML(reediciones[item])
            if "Por problemas de imprenta" in reediciones[item]:
                problemaImpresion.append(reediciones[item])
                reediciones.pop()
    except:
        reediciones = None
    # Si hay un aviso, elimino el ultimó elemento de la lista que lo encontró. Si llega a haber más de un aviso hay
    # que reimplementar esa solución.
    return [lanzamientos, reediciones, problemaImpresion]


def parseLanzamiento(body):
    parrafos = re.findall(r'<p>(.*?)</p>', body)
    bulletpoints = parrafos[0].split("<br />")
    for x in range(len(bulletpoints)):
        bulletpoints[x] = stripHTML(bulletpoints[x])
    bulletpoints = list(filter(None, bulletpoints))
    return bulletpoints


# Tomamos el primer parrafo del texto.
def parseOtro(body):
    try:
        contenido = re.findall(r'<p>(.*?)</p>', body)[0]
    except:
        contenido = re.findall(r'>(.*?)</h\d>', body)[0]
    contenido = stripHTML(contenido)

    return contenido


def parseResumenAnuncios(body):
    anuncios = []
    items = re.findall(r'<p>(.*?)</p>', body)
    # Viejo formato para el resumen de anuncios. Ver si es relevante en un futuro.
    if items:
        for parrafo in items:
            anuncios.append(re.findall(r'<strong>(.*?)</strong>', parrafo))
        anuncios = list(filter(None, anuncios))
        for x in range(len(anuncios)):
            for i in range(len(anuncios[x])):
                anuncios[x][i] = anuncios[x][i].split("&#8211;")
                anuncios[x][i] = list(filter(None, anuncios[x][i]))
            anuncios[x] = list(itertools.chain.from_iterable(anuncios[x]))
    # Nueva formato (10/8/24). Ver si se repite este formato
    else:
        items = re.findall(r'(?s)(?<=<ul class=\"wp-block-list\">).*?(?=</ul>)', body)
        for item in items:
            lineaItem = [re.search(r'<strong>(.*?)</strong>', item).group()]
            bulletpoints = item.split("&#8211;")
            bulletpoints[0] = re.sub(r"<a(.*?)</a>", ' ', bulletpoints[0])
            for line in bulletpoints: lineaItem.append(stripHTML(line))
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
def deleteReedicionesFromGroupImgs(list, start):
    return list[:start]


# Devuelve un array con todas las imgs de los mangas que salieron hoy
def fetchGroupImgs(article):
    return re.findall(r'src=\"(.*?)\"', article)


# Para darle formato a las novedades, vamos a poner el titulo, link, y cada manga que sale en una lista
def formatNovedades(entry):
    tipo = "Photo"
    titulo = entry.title
    link = entry.link
    contenido = parseTitlesNovedades(entry.content[0]['value'])
    imagen = fetchGroupImgs(entry.content[0]['value'])
    # Puede que hayan multiples imágenes. En ese caso vemos si son más de una (ignorando reediciones) y categorizamos
    # el post según corresponda
    if len(imagen) > 1 and any("(reedición)" in titulo.casefold() for titulo in contenido):
        imagen = imagen[:-1]
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
    listaFinal = {
        "tipo": tipo,
        "titulo": titulo,
        "link": link,
        "media": imagen,
        "contenido": contenido
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
    elif len(imagenes) < len(contenido):
        contenido = contenido[:len(imagenes)]
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
    elif "ivrea publicar" in articulo.title.casefold() or articulo.content[0]['value'].count("<br />") > 2:
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
            msg = convertMsg.msgLanzamiento(articulo["titulo"], articulo["link"], articulo["contenido"])
        case "Resumen":
            articulo = formatResumenAnuncios(entry)
            msg = convertMsg.msgResumen(articulo["titulo"], articulo["link"], articulo["contenido"])
        case "Otro":
            articulo = formatOtro(entry)
            msg = convertMsg.msgOtro(articulo["titulo"], articulo["link"], articulo["contenido"])
    articulo["mensaje"] = msg
    return articulo
