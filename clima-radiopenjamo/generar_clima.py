
import json
import urllib.request
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

CARPETA = Path(__file__).resolve().parent
GUION = CARPETA / "guion_clima.txt"

LATITUD = 20.4311
LONGITUD = -101.7226

URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUD}&longitude={LONGITUD}"
    "&current=temperature_2m,relative_humidity_2m,"
    "apparent_temperature,weather_code,wind_speed_10m"
    "&daily=temperature_2m_max,temperature_2m_min,"
    "precipitation_probability_max"
    "&timezone=America%2FMexico_City"
    "&forecast_days=1"
)

def descripcion(codigo):
    if codigo == 0:
        return "cielo despejado"
    if codigo in (1, 2, 3):
        return "cielo parcialmente nublado o nublado"
    if codigo in (45, 48):
        return "presencia de niebla"
    if codigo in (51, 53, 55, 56, 57):
        return "posibilidad de lloviznas"
    if codigo in (61, 63, 65, 66, 67, 80, 81, 82):
        return "condiciones de lluvia"
    if codigo in (95, 96, 99):
        return "posibilidad de tormentas electricas"
    return "condiciones meteorologicas variables"

def generar():
    solicitud = urllib.request.Request(
        URL,
        headers={"User-Agent": "RadioPenjamoClima/1.0"}
    )

    with urllib.request.urlopen(
        solicitud, timeout=30
    ) as respuesta:
        datos = json.load(respuesta)

    actual = datos["current"]
    diario = datos["daily"]

    temperatura = round(actual["temperature_2m"])
    sensacion = round(actual["apparent_temperature"])
    humedad = actual["relative_humidity_2m"]
    viento = round(actual["wind_speed_10m"])
    estado = descripcion(actual["weather_code"])

    maxima = round(diario["temperature_2m_max"][0])
    minima = round(diario["temperature_2m_min"][0])
    lluvia = diario["precipitation_probability_max"][0]

    ahora = datetime.now(
        ZoneInfo("America/Mexico_City")
    )

    fecha = ahora.strftime("%d/%m/%Y")

    texto = f"""
Radio Penjamo presenta su reporte del clima.

Muy buenos dias, tardes o noches, amigos radioescuchas.

Les presentamos la informacion meteorologica
para Penjamo, Guanajuato, correspondiente
al dia {fecha}.

Actualmente tenemos una temperatura
de {temperatura} grados centigrados,
con sensacion termica de {sensacion} grados.

Las condiciones del cielo indican {estado}.

La humedad relativa es del {humedad} por ciento,
y el viento alcanza los {viento} kilometros por hora.

Para este dia se pronostica una temperatura
maxima de {maxima} grados,
y una minima de {minima} grados centigrados.

La probabilidad maxima de precipitacion
prevista para hoy es del {lluvia} por ciento.

Recuerde tomar sus precauciones
ante los cambios de temperatura.

Desde Penjamo, Guanajuato,
para Mexico y el mundo.

Esto fue el reporte meteorologico
de Radio Penjamo.

Juntando familias gracias a la magia de la radio.
"""

    GUION.write_text(
        texto.strip(),
        encoding="utf-8"
    )

    print("GUION DEL CLIMA GENERADO CORRECTAMENTE")
    print(f"Archivo: {GUION}")

if __name__ == "__main__":
    generar()

