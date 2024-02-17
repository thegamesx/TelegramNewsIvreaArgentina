import re

lineBreak = "\n"

"""
def msgNovedades(title,link,content):
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 saltos de linea
    msg += lineBreak + lineBreak
    # Inserta los titulos
    for manga in content:
        if "(REEDICIÓN)" in manga[0]:
            emoji = "\U0001F504" #Flechas circulares
        else:
            emoji = "\U0001F4D6" #Libro abierto
        msg += emoji + " <b>" + manga[0] + "</b>" + lineBreak
        for subtitulos in manga[1:]:
            msg += "  - " + subtitulos + lineBreak
        msg += lineBreak
    # Por ultimo, insertamos el link
    msg += "<a href=\"" + link + "\">Leer más</a>"

    return msg
"""

def msgNovedades(title,link,content):
    firstReedicion=False
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 saltos de linea
    msg += lineBreak + lineBreak
    # Inserta los titulos
    for manga in content:
        if "(REEDICIÓN)" in manga:
            emoji = "\U0001F504"  # Flechas circulares
            if firstReedicion==False:
                # Separamos las reediciones
                msg += lineBreak + "<b>REEDICIONES</b>" + lineBreak + lineBreak
                firstReedicion=True
        else:
            emoji = "\U0001F4D6"  # Libro abierto
        msg += emoji + " " + manga + lineBreak
    # Por ultimo, insertamos el link
    msg += lineBreak + "<a href=\"" + link + "\">Leer más</a>"

    return msg

def msgSalioHoy(title,link,content):
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 saltos de linea
    msg += lineBreak + lineBreak
    # Inserta los titulos
    for manga in content[0]:
        msg += "\U0001F4D6" + " " + manga + lineBreak
    #Separamos las reediciones
    msg += lineBreak + "<b>REEDICIONES</b>" + lineBreak + lineBreak
    for manga in content[1]:
        msg += "\U0001F504" + " " + manga + lineBreak
    # Por ultimo, insertamos el link
    msg += lineBreak + "<a href=\"" + link + "\">Leer más</a>"

    return msg

def msgLanzamiento(title, link, bulletpoints):
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 saltos de linea
    msg += lineBreak + lineBreak
    #Primero sabemos que el primero siempre es el titulo, asi que insertamos eso
    msg += "\U0001F4D6" + " <b>" + bulletpoints[0] + "</b>" + lineBreak
    #Y luego vemos si el siguiente es el nombre original. En caso de no tenerlo, se sigue con el resto
    if bulletpoints[1][:3] != "De ":
        msg += "\U0001F1EF\U0001F1F5" + " " + bulletpoints[1] + lineBreak
        eliminar=2
    else:
        eliminar=1
    # Inserta los detalles, eliminando los que ya insertamos arriba
    for linea in bulletpoints[eliminar:]:
        #Aca vamos a ver que emoji usar, dependiendo del contenido.
        if linea[:3] == "De " or "escrita por" in linea.casefold():
            emoji = "\u270F" #Lapiz (autor)
        elif "serie de" in linea.casefold() or "novela compuesta" in linea.casefold() or "tomo único" in linea.casefold():
            emoji = "\U0001F4DA" #Pila de libros (duracion)
        elif "formato " in linea.casefold():
            emoji = "\U0001F4C4" #Hoja (Formato)
        elif "a la venta" in linea.casefold() or "salida" in linea.casefold():
            emoji = "\u23F0" #Reloj despertador (Lanzamiento)
        #Considerar cambiar esto
        elif "shonen" == linea.casefold() or "seinen" == linea.casefold() or "shojo" == linea.casefold() or "bl/yaoi" == linea.casefold() or "josei" == linea.casefold() or "yuri" == linea.casefold():
            emoji = "\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466" #Familia (genero)
        else:
            emoji = "\u2705" #Tick (otro)
        msg += emoji + " " + linea + lineBreak
    # Por ultimo, insertamos el link
    msg += lineBreak + "<a href=\"" + link + "\">Leer más</a>"

    return msg

def msgResumen(title, link, content):
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 saltos de linea
    msg += lineBreak + lineBreak
    for newManga in content:
        # Primero sabemos que el primero siempre es el titulo, asi que insertamos eso
        msg += "\U0001F4D6" + " <b>" + newManga[0] + "</b>" + lineBreak
        for linea in newManga[1:]:
        # El segundo deberia ser el formato, pero chequeamos por las dudas
            if "formato " in linea.casefold():
                emoji = "\U0001F4C4"  # Hoja (Formato)
            elif "a la venta" in linea.casefold():
                emoji = "\u23F0" #Reloj despertador (Lanzamiento)
            else:
                emoji = "\u2705"  # Tick (otro)
            msg += emoji + linea + lineBreak
        msg += lineBreak
    # Por ultimo, insertamos el link
    msg += lineBreak + "<a href=\"" + link + "\">Leer más</a>"
    return msg

def msgOtro(title, link, content):
    # Inserta el título
    msg = "<b>" + title + "</b>"
    # Inserta 2 salto de linea
    msg += lineBreak + lineBreak
    # Inserta el contenido
    msg+= content + lineBreak
    # Por ultimo, insertamos el link
    msg += lineBreak + "<a href=\"" + link + "\">Leer más</a>"

    return msg