	
import json
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
DESTINO = CARPETA / "noticias_regionales.json"

FUENTES = {
    "Pénjamo TV": "https://www.penjamotv.com/feed/",
    "Notus": "https://notus.com.mx/feed/",
    "Notus página 2": "https://notus.com.mx/feed/?paged=2",
    "Notus página 3": "https://notus.com.mx/feed/?paged=3",
    "Notus página 4": "https://notus.com.mx/feed/?paged=4",
    "Notus página 5": "https://notus.com.mx/feed/?paged=5"
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

            es_local = any(
                localidad in texto_noticia
                for localidad in LOCALIDADES
            )

            temas_estatales = [
                "vacun", "salud", "influenza",
                "educacion", "escuela", "primaria",
                "secundaria", "beca", "apoyos",
                "mujeres rurales", "agricult", "campo"
            ]

            es_estatal = (
                "guanajuato" in titulo_normalizado
                and any(
                    tema in titulo_normalizado
                    for tema in temas_estatales
                )
            )

            if not es_local and not es_estatal:
                continue

            if enlace in enlaces:
                continue

            enlaces.add(enlace)

            resultados.append({
                "prioridad": 0 if es_local else 1,
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
