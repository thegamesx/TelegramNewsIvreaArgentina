lineBreak = "\n"


def msgNovedades(title, link, content):
    firstReedicion = False
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 saltos de línea
    msg += lineBreak + lineBreak
    # Inserta los títulos
    for manga in content:
        if "(reedición)" in manga.casefold() or "(reediciones)" in manga.casefold():
            emoji = "\U0001F504"  # Flechas circulares
            if not firstReedicion:
                # Separamos las reediciones
                msg += lineBreak + "<b>REEDICIONES</b>" + lineBreak + lineBreak
                firstReedicion = True
            mangaTitle = manga.replace("(REEDICIÓN)", "")
            mangaTitle = mangaTitle.replace("(REEDICIONES)", "")
        else:
            emoji = "\U0001F4D6"  # Libro abierto
            mangaTitle = manga
        msg += emoji + " " + mangaTitle + lineBreak
    # Por ultimo, insertamos el link
    msg += lineBreak + "<a href=\"" + link + "\">Leer más</a>"

    return msg


def msgSalioHoy(title, link, content):
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 saltos de línea
    msg += lineBreak + lineBreak
    # Inserta los titulos
    for manga in content[0]:
        msg += "\U0001F4D6" + " " + manga + lineBreak
    # Separamos las reediciones, si las hay
    if content[1]:
        msg += lineBreak + "<b>REEDICIONES</b>" + lineBreak + lineBreak
        for manga in content[1]:
            msg += "\U0001F504" + " " + manga + lineBreak
    # Vemos si hubo algún problema con las impresiones. De ser asi agregamos un aviso
    if content[2]:
        msg += lineBreak
        for aviso in content[2]:
            msg += "\u203C " + aviso + lineBreak
    # Por ultimo, insertamos el link
    msg += lineBreak + "<a href=\"" + link + "\">Leer más</a>"

    return msg


def msgLanzamiento(title, link, bulletpoints, linksExternos):
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 saltos de línea
    msg += lineBreak + lineBreak
    # Primero sabemos que el primero siempre es el título, asi que insertamos eso
    msg += "\U0001F4D6" + " <b>" + bulletpoints[0] + "</b>" + lineBreak
    # Y luego vemos si el siguiente es el nombre original. En caso de no tenerlo, se sigue con el resto
    if bulletpoints[1][:3].casefold() != "de " or "escrita por" in bulletpoints[1].casefold():
        msg += "\U0001F1EF\U0001F1F5" + " " + bulletpoints[1] + lineBreak
        eliminar = 2
    else:
        eliminar = 1
    # Inserta los detalles, eliminando los que ya insertamos arriba
    for linea in bulletpoints[eliminar:]:
        # Aca vamos a ver qué emoji usar, dependiendo del contenido.
        if linea[:3].casefold() == "de " or "escrita por" in linea.casefold():
            emoji = "\u270F"  # Lápiz (autor)
        elif (
                "serie de" in linea.casefold() or
                "novela compuesta" in linea.casefold() or
                "tomo único" in linea.casefold() or
                "tomos de" in linea.casefold() or
                "libro de" in linea.casefold()
        ):
            emoji = "\U0001F4DA"  # Pila de libros (duración)
        elif "formato " in linea.casefold():
            emoji = "\U0001F4C4"  # Hoja (Formato)
        elif "a la venta" in linea.casefold() or "salida" in linea.casefold():
            emoji = "\u23F0"  # Reloj despertador (Lanzamiento)
        # Considerar cambiar esto
        elif ("shonen" == linea.casefold() or
              "seinen" == linea.casefold() or
              "shojo" == linea.casefold() or
              "bl/yaoi" == linea.casefold() or
              "josei" == linea.casefold() or
              "yuri" == linea.casefold()):
            emoji = "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466"  # Familia (genero)
        else:
            emoji = "\u2705"  # Tick (otro)
        msg += emoji + " " + linea + lineBreak
    if linksExternos["anilist"] or linksExternos["MAL"]:
        msg += lineBreak
    # Insertamos links a Anilist y MAL, si encuentra la serie en cuestión
    if linksExternos["anilist"]:
        msg += "\u27A1\uFE0F " + "<a href=\"https://anilist.co/manga/" + str(
            linksExternos["anilist"]) + "\">Anilist</a>" + lineBreak
    if linksExternos["MAL"]:
        msg += "\u27A1\uFE0F " + "<a href=\"https://myanimelist.net/manga/" + str(
            linksExternos["MAL"]) + "\">MyAnimeList</a>" + lineBreak
    # Por ultimo, insertamos el link
    msg += lineBreak + "<a href=\"" + link + "\">Leer más</a>"

    return msg


def msgResumen(title, link, content):
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 saltos de línea
    msg += lineBreak + lineBreak
    for newManga in content:
        # Las primeras dos líneas incluyen un link y el título, asi que las combinamos de la sig forma
        msg += "\U0001F4D6" + "<a href=" + newManga[0] + "><b>" + newManga[1] + "</b></a>" + lineBreak
        for linea in newManga[2:]:
            # El segundo debería ser el formato, pero chequeamos por las dudas
            if "formato " in linea.casefold():
                emoji = "   \U0001F4C4 "  # Hoja (Formato)
            elif "a la venta" in linea.casefold() or "salida" in linea.casefold():
                emoji = "   \u23F0 "  # Reloj despertador (Lanzamiento)
            elif (
                    "serie de" in linea.casefold() or
                    "novela compuesta" in linea.casefold() or
                    "tomo único" in linea.casefold() or
                    "tomos de" in linea.casefold() or
                    "libro de" in linea.casefold() or
                    "nueva serie" in linea.casefold()
            ):
                emoji = "   \U0001F4DA "  # Pila de libros (duración)
            else:
                emoji = "   \u2705 "  # Tick (otro)
            msg += emoji + linea + lineBreak
        msg += lineBreak
    # Por ultimo, insertamos el link
    msg += "<a href=\"" + link + "\">Leer más</a>"

    return msg


def msgOtro(title, link, content):
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 salto de linea
    msg += lineBreak + lineBreak
    # Inserta el contenido
    msg += content + lineBreak
    # Por ultimo, insertamos el link
    msg += lineBreak + "<a href=\"" + link + "\">Leer más</a>"

    return msg
