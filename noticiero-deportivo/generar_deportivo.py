
import json
from pathlib import Path
from datetime import datetime, timedelta

CARPETA = Path(__file__).resolve().parent
ARCHIVO_NOTICIAS = CARPETA / "Noticias" / "noticias_deportivas.json"
ARCHIVO_GUION = CARPETA / "guion_deportivo.txt"

print("Preparando Radio Pénjamo Deportes...")

with open(ARCHIVO_NOTICIAS, encoding="utf-8") as archivo:
    noticias = json.load(archivo)


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
    "Presentamos Radio Pénjamo Deportes.",
    "La información deportiva de México y el mundo."
]

for prioridad, fecha, titulo, resumen in seleccionadas[:10]:
    tipo = "Información deportiva"
    if resumen:
        guion.append(f"{tipo}. {titulo}. {resumen}")
    else:
        guion.append(f"{tipo}. {titulo}.")


if len(seleccionadas) == 0:
    print("SIN NOTICIAS DEPORTIVAS DISPONIBLES")
    raise SystemExit(1)


guion.append(
    "Hasta aquí nuestro resumen deportivo. "
    "Radio Pénjamo, juntando familias gracias "
    "a la magia de la radio."
)

guion = [linea.replace("**%**", "").replace(r"\*\*%\*\*", "").strip() for linea in guion]
ARCHIVO_GUION.write_text(
    "\n\n".join(guion),
    encoding="utf-8"
)

print("GUION DEPORTIVO GENERADO CORRECTAMENTE")
print("Noticias recientes:", min(len(seleccionadas), 10))
print("Archivo:", ARCHIVO_GUION)
