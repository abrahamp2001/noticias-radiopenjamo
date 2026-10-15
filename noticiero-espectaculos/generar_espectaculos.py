import json
import re
from pathlib import Path
from datetime import datetime

CARPETA = Path(__file__).resolve().parent
ENTRADA = CARPETA / "Noticias" / "noticias_espectaculos.json"
SALIDA = CARPETA / "guion_espectaculos.txt"

with open(ENTRADA, encoding="utf-8") as archivo:
    noticias = json.load(archivo)

if not noticias:
    raise SystemExit("SIN NOTICIAS: no se genera el guion.")

secciones = {
    "TVNotas": [],
    "Ventaneando": [],
    "Rolling Stone": []
}

for noticia in noticias:
    fuente = noticia.get("fuente", "")
    titulo = noticia.get("titulo", "").strip()

    if fuente in secciones and titulo:
        titulo = re.sub(r"\s+-\s+(TVNotas|TV Azteca)$", "", titulo)
        secciones[fuente].append(titulo)

guion = [
    "¡Atención, atención, mi gente bonita!",
    "¡Porque aquí los secretos no se guardan, las noticias se cuentan!",
    "Desde Radio Pénjamo, ciento cinco punto cinco FM, la Finísima...",
    "¡Arranca Se Armó la Farándula!",
    "Yo soy Salomé, y hoy venimos con música, televisión, artistas y muchas novedades.",
    "Así que acomódense, suban el volumen y vámonos con todo.",
    "¡Que comience el espectáculo!"
]

presentaciones = {
    "TVNotas": "Comenzamos con las novedades de la farándula mexicana, de acuerdo con TVNotas.",
    "Ventaneando": "Y ahora abrimos nuestra ventana al espectáculo, con información publicada por TV Azteca y relacionada con Ventaneando.",
    "Rolling Stone": "Nos vamos al mundo de la música internacional, con titulares publicados por Rolling Stone."
}

comentarios = [
    "¡Ay, mi gente! Aquí seguimos pendientes de lo que sucede en el espectáculo.",
    "¡Y espérense, porque todavía tenemos más novedades!",
    "¡Esto está más movido que pista de baile en sábado por la noche!",
    "¡Qué cosas pasan en el mundo de la farándula!",
    "¡Seguimos con más noticias, porque aquí nadie se queda sin enterarse!"
]

contador = 0

for fuente, titulos in secciones.items():
    if not titulos:
        continue

    guion.append(presentaciones[fuente])

    for titulo in titulos:
        contador += 1
        guion.append(
            "Entre los titulares que publica "
            + fuente
            + ", encontramos lo siguiente. "
            + titulo
        )

        if contador % 3 == 0:
            guion.append(comentarios[(contador // 3 - 1) % len(comentarios)])

guion.extend([
    "Y así llegamos al final de esta edición de Se Armó la Farándula.",
    "Recuerden que algunos titulares pueden referirse a rumores o declaraciones, y no necesariamente a hechos confirmados.",
    "Yo soy Salomé y les agradezco de corazón por acompañarnos.",
    "Nos escuchamos en nuestra próxima edición.",
    "Radio Pénjamo, ciento cinco punto cinco FM.",
    "Juntando familias gracias a la magia de la radio.",
    "¡Besitos, mi gente bonita, y que siga el espectáculo!"
])

SALIDA.write_text("\n\n".join(guion), encoding="utf-8")

print("GUION DE ESPECTACULOS GENERADO CORRECTAMENTE")
print("NOTICIAS INCLUIDAS:", contador)
print("PALABRAS:", len(" ".join(guion).split()))
print("ARCHIVO:", SALIDA)
