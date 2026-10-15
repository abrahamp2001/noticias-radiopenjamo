import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
DESTINO = CARPETA / "noticias_espectaculos.json"

FUENTES = {
    "Rolling Stone": "https://www.rollingstone.com/feed/",
    "TVNotas": "https://news.google.com/rss/search?q=site%3Atvnotas.com.mx&hl=es-419&gl=MX&ceid=MX%3Aes-419",
    "Ventaneando": "https://news.google.com/rss/search?q=Ventaneando%20espectaculos%20when%3A2d&hl=es-419&gl=MX&ceid=MX%3Aes-419"
}

ahora = datetime.now(timezone.utc)
limite = ahora - timedelta(hours=48)
resultados = []

for medio, url in FUENTES.items():
    print("CONSULTANDO:", medio)
    try:
        solicitud = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(solicitud, timeout=15) as respuesta:
            contenido = respuesta.read()

        raiz = ET.fromstring(contenido)

        for noticia in raiz.findall(".//channel/item"):
            titulo = noticia.findtext("title", "").strip()
            enlace = noticia.findtext("link", "").strip()
            fecha = noticia.findtext("pubDate", "").strip()

            try:
                publicada = parsedate_to_datetime(fecha)
                publicada = publicada.astimezone(timezone.utc)
            except (ValueError, TypeError):
                continue

            if titulo and enlace and limite <= publicada <= ahora:
                resultados.append({
                    "titulo": titulo,
                    "fuente": medio,
                    "url": enlace,
                    "fecha": publicada.isoformat()
                })

    except Exception as error:
        print("ERROR:", error)

resultados.sort(key=lambda n: n["fecha"], reverse=True)

cupos = {"TVNotas": 8, "Ventaneando": 7, "Rolling Stone": 5}
seleccionadas = []

for fuente, cantidad in cupos.items():
    noticias_fuente = [
        n for n in resultados if n["fuente"] == fuente
    ]
    seleccionadas.extend(noticias_fuente[:cantidad])

seleccionadas.sort(key=lambda n: n["fecha"], reverse=True)

DESTINO.write_text(
    json.dumps(seleccionadas, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("NOTICIAS DE ESPECTACULOS:", len(seleccionadas))
