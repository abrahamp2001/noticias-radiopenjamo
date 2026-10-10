
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

# Noticias nacionales de Google Noticias México
RSS_URL = (
    "https://news.google.com/rss?"
    "hl=es-419&gl=MX&ceid=MX:es-419"
)

ARCHIVO = "noticias.json"
MAX_NOTICIAS = 20


def limpiar_html(texto):
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    texto = unescape(texto)
    return " ".join(texto.split())


def obtener_texto(elemento, nombre):
    nodo = elemento.find(nombre)
    if nodo is not None and nodo.text:
        return nodo.text.strip()
    return ""


def convertir_fecha(fecha):
    try:
        fecha_dt = parsedate_to_datetime(fecha)
        return fecha_dt.strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return fecha


def obtener_imagen(item):
    # Algunos canales RSS incluyen imagen;
    # otros solo ofrecen titulares.
    espacios = [
        "{http://search.yahoo.com/mrss/}thumbnail",
        "{http://search.yahoo.com/mrss/}content",
    ]

    for nombre in espacios:
        nodo = item.find(nombre)
        if nodo is not None:
            url = nodo.get("url", "")
            if url.startswith("https://"):
                return url

    enclosure = item.find("enclosure")
    if enclosure is not None:
        tipo = enclosure.get("type", "")
        url = enclosure.get("url", "")
        if tipo.startswith("image/") and url.startswith("https://"):
            return url

    return ""


def actualizar():
    peticion = urllib.request.Request(
        RSS_URL,
        headers={
            "User-Agent": "Mozilla/5.0 RadioPenjamoNoticias/1.0"
        }
    )

    with urllib.request.urlopen(
        peticion, timeout=30
    ) as respuesta:
        contenido = respuesta.read()

    raiz = ET.fromstring(contenido)
    noticias = []

    for item in raiz.findall("./channel/item"):
        titulo = limpiar_html(obtener_texto(item, "title"))
        enlace = obtener_texto(item, "link")
        fecha = obtener_texto(item, "pubDate")

        if not titulo or not enlace.startswith("https://"):
            continue

        fuente = obtener_texto(item, "source")
        descripcion = (
            "Consulta la información completa en la fuente "
            "original."
        )

        if fuente:
            descripcion = (
                "Información publicada por "
                + fuente
                + ". Consulta la nota completa."
            )

        noticias.append({
            "titulo": titulo,
            "descripcion": descripcion,
            "fecha": convertir_fecha(fecha),
            "imagen": obtener_imagen(item),
            "enlace": enlace
        })

        if len(noticias) >= MAX_NOTICIAS:
            break

    if not noticias:
        raise RuntimeError(
            "No se encontraron noticias. "
            "Se conservará el archivo anterior."
        )

    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(
            noticias,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"Actualización completada: "
        f"{len(noticias)} noticias."
    )


if __name__ == "__main__":
    actualizar()
