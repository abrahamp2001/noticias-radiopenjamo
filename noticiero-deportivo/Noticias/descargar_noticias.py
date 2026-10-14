	
import json
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
DESTINO = CARPETA / "noticias_deportivas.json"

FUENTES = {
    "ESPN Deportes": "https://espndeportes.espn.com/espn/rss/news",
}

LOCALIDADES = [
    "penjamo", "abasolo", "huanimaro", "cueramaro",
    "la piedad", "santa ana pacueco", "corralejo",
    "trojes de maranon", "zapote de la esperanza",
    "santa fe del rio", "estacion corralejo",
    "guayabo de origel", "magallanes",
    "estacion penjamo", "potreros"
]

def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.casefold())
    return "".join(
        letra for letra in texto
        if unicodedata.category(letra) != "Mn"
    )

ahora = datetime.now(timezone.utc)
limite = ahora - timedelta(hours=24)

resultados = []
enlaces = set()
fuentes_correctas = 0

for medio, url in FUENTES.items():
    print("CONSULTANDO:", medio)

    try:
        solicitud = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(
            solicitud, timeout=15
        ) as respuesta:
            contenido = respuesta.read()

        raiz = ET.fromstring(contenido)
        noticias = raiz.findall(".//channel/item")
        fuentes_correctas += 1

        for noticia in noticias:
            titulo = noticia.findtext("title", "").strip()
            fecha = noticia.findtext("pubDate", "").strip()
            enlace = noticia.findtext("link", "").strip()

            if not titulo or not enlace:
                continue

            try:
                publicada = parsedate_to_datetime(fecha)
                publicada = publicada.astimezone(timezone.utc)
            except (ValueError, TypeError):
                continue

            if not limite <= publicada <= ahora:
                continue

            descripcion = noticia.findtext("description", "")
            texto_noticia = normalizar(titulo + " " + descripcion)
            titulo_normalizado = normalizar(titulo)

            es_local = False

            if enlace in enlaces:
                continue

            enlaces.add(enlace)

            resultados.append({
                "prioridad": 1,
                "titulo": titulo,
                "fecha": publicada.astimezone().strftime(
                    "%d/%m/%Y %H:%M"
                ),
                "fuente": medio,
                "url": enlace
            })

    except Exception as error:
        print("ERROR EN", medio, ":", error)

if fuentes_correctas == 0:
    raise SystemExit(
        "ERROR: No se pudo consultar ninguna fuente."
    )

resultados.sort(
    key=lambda noticia: (
        noticia["prioridad"],
        -datetime.strptime(
            noticia["fecha"], "%d/%m/%Y %H:%M"
        ).timestamp()
    )
)

anteriores = {}
if DESTINO.exists():
    try:
        for nota in json.loads(DESTINO.read_text(encoding="utf-8")):
            anteriores[nota["url"]] = nota.get("resumen", "")
    except (ValueError, KeyError, TypeError):
        print("AVISO: No se pudieron recuperar los resúmenes anteriores.")

for nota in resultados:
    nota["resumen"] = anteriores.get(nota["url"], "")

DESTINO.write_text(
    json.dumps(
        resultados[:10],
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

print("DESCARGA REGIONAL FINALIZADA")
print("NOTICIAS ENCONTRADAS:", len(resultados[:10]))

for noticia in resultados[:10]:
    print("-", noticia["titulo"])
