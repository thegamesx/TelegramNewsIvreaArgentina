import urllib.request

url = "https://www.ivreality.com.ar/feed/"
archivo_destino = "feed_prueba.xml"

try:
    # Descarga el contenido del feed y lo guarda en un archivo local
    urllib.request.urlretrieve(url, archivo_destino)
    print(f"¡Feed guardado con éxito en '{archivo_destino}'!")
except Exception as e:
    print(f"Error al descargar el feed: {e}")