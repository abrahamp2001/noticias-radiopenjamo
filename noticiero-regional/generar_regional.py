
import json
from pathlib import Path
from datetime import datetime, timedelta

CARPETA = Path(__file__).resolve().parent
ARCHIVO_NOTICIAS = CARPETA / "Noticias" / "noticias_regionales.json"
ARCHIVO_HISTORIAS = CARPETA / "Historias" / "historias.json"
ARCHIVO_GUION = CARPETA / "guion_regional.txt"

print("Preparando Noticiero Regional de Radio Pénjamo...")

with open(ARCHIVO_NOTICIAS, encoding="utf-8") as archivo:
    noticias = json.load(archivo)

with open(ARCHIVO_HISTORIAS, encoding="utf-8") as archivo:
    historias = json.load(archivo)

ahora = datetime.now()
limite = ahora - timedelta(hours=24)

seleccionadas = []

for noticia in noticias:
    try:
        fecha = datetime.strptime(
            noticia.get("fecha", ""), "%d/%m/%Y %H:%M"
        )
        titulo = noticia.get("titulo", "").strip()
        if limite <= fecha <= ahora and titulo:
            seleccionadas.append((noticia.get("prioridad", 1), fecha, titulo, noticia.get("resumen", "").strip()))
    except (ValueError, TypeError, AttributeError):
        continue

seleccionadas.sort(key=lambda n: (n[0], -n[1].timestamp()))

import os
if os.environ.get("RADIO_AUTOMATICO") == "SI" and not seleccionadas:
    raise SystemExit("SIN NOTICIAS RECIENTES: publicación automática cancelada.")


guion = [
    "Radio Pénjamo, ciento cinco punto cinco FM.",
    "La Finísima.",
    "Presentamos Radio Pénjamo Informa, Nuestra Región.",
    "Las noticias de Pénjamo y los municipios vecinos."
]

for prioridad, fecha, titulo, resumen in seleccionadas[:20]:
    tipo = "Noticia regional" if prioridad == 0 else "Información estatal"
    if resumen:
        guion.append(f"{tipo}. {titulo}. {resumen}")
    else:
        guion.append(f"{tipo}. {titulo}.")

espacios = 10 - min(len(seleccionadas), 10)

if espacios > 0 and historias:
    guion.append(
        "Y ahora, conozcamos un poco de la historia "
        "de nuestra región."
    )

    for historia in historias[:espacios]:
        titulo = historia.get("titulo", "").strip()
        texto = historia.get("texto", "").strip()
        if titulo and texto:
            guion.append(f"Cápsula histórica. {titulo}. {texto}")

if len(guion) == 4:
    print("Todavía no hay noticias ni historias disponibles.")
    raise SystemExit(0)

guion.append(
    "Hasta aquí nuestro resumen informativo regional. "
    "Radio Pénjamo, juntando familias gracias "
    "a la magia de la radio."
)

guion = [linea.replace("**%**", "").replace("\\*\\*%\\*\\*", "") for linea in guion]
ARCHIVO_GUION.write_text(
    "\n\n".join(guion),
    encoding="utf-8"
)

print("GUION REGIONAL GENERADO CORRECTAMENTE")
print("Noticias recientes:", min(len(seleccionadas), 10))
print("Archivo:", ARCHIVO_GUION)
