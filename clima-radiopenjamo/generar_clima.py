
import json
import urllib.request
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# RADIO PENJAMO - NOTICIERO DEL CLIMA

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
    condiciones = {
        0: "cielo despejado",
        1: "cielo mayormente despejado",
        2: "cielo parcialmente nublado",
        3: "cielo nublado",
        45: "presencia de niebla",
        48: "presencia de niebla",
        51: "llovizna ligera",
        53: "llovizna moderada",
        55: "llovizna intensa",
        61: "lluvia ligera",
        63: "lluvia moderada",
        65: "lluvia intensa",
        80: "chubascos ligeros",
        81: "chubascos moderados",
        82: "chubascos intensos",
        95: "tormentas electricas",
        96: "tormentas con granizo",
        99: "tormentas fuertes con granizo"
    }
    return condiciones.get(
        codigo, "condiciones meteorologicas variables"
    )

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

    if 5 <= ahora.hour < 12:
        saludo = "Muy buenos días"
    elif 12 <= ahora.hour < 19:
        saludo = "Muy buenas tardes"
    else:
        saludo = "Muy buenas noches"

    texto = (
        f"Radio Pénjamo presenta el reporte del clima. "
        f"{saludo} amigos radioescuchas. "
        f"Les compartimos las condiciones del tiempo "
        f"para Pénjamo Guanajuato este {fecha}. "
        f"Actualmente tenemos {temperatura} grados "
        f"centígrados con sensación térmica "
        f"de {sensacion} grados. "
        f"El cielo presenta {estado}. "
        f"La humedad es del {humedad} por ciento "
        f"y los vientos alcanzan los {viento} "
        f"kilómetros por hora. "
        f"Para hoy se espera una temperatura máxima "
        f"de {maxima} grados y una mínima "
        f"de {minima} grados. "
        f"La probabilidad máxima de lluvia "
        f"es del {lluvia} por ciento. "
        f"Le recomendamos tomar precauciones "
        f"ante los cambios de temperatura "
        f"y mantenerse informado. "
        f"Desde Pénjamo Guanajuato esto fue "
        f"el reporte meteorológico de Radio Pénjamo. "
        f"Juntando familias gracias a la magia de la radio."
    )

    GUION.write_text(texto, encoding="utf-8")

    print("REPORTE DEL CLIMA GENERADO CORRECTAMENTE")
    print(f"Guion guardado en: {GUION}")

if __name__ == "__main__":
    generar()
