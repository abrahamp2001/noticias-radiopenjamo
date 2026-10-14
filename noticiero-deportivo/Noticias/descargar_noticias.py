"""Descarga titulares deportivos recientes para Radio Pénjamo Deportes.

No altera archivos ni procesos del Noticiero Regional.
"""
import json
import re
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
DESTINO = CARPETA / "noticias_deportivas.json"
FUENTES = {
    "Google Noticias Deportes": "https://news.google.com/rss/search?q=deportes+Mexico&hl=es-419&gl=MX&ceid=MX:es-419"
}

# Se excluyen espectáculos y usos no deportivos de la palabra «deportes».
EXCLUIR = (
    "concierto", "setlist", "gira musical", "palacio de los deportes",
    "festival musical", "estreno musical", "cantante",
    "banda de rock", "album musical", "cartelera de espectaculos",
)

# Indicios deportivos: evita aceptar cualquier noticia por mencionar «deportes».
DEPORTES = (
    "futbol", "liga mx", "liguilla", "seleccion mexicana", "mundial", "premundial",
    "champions", "concacaf", "uefa", "fifa", "gol", "goles", "partido",
    "marcador", "cancha", "estadio", "jugador", "jugadora", "entrenador",
    "tecnico", "club america", "chivas", "cruz azul", "pumas", "tigres",
    "rayados", "toluca", "leon", "jamaica", "basquetbol", "nba", "beisbol",
    "mlb", "serie mundial", "dodgers", "yankees", "nfl", "super bowl",
    "tochito", "flag football", "formula 1", "formula uno", "f1", "gran premio",
    "automovilismo", "boxeo", "boxeador", "ufc", "mma", "tenis", "atp",
    "wta", "ciclismo", "ciclista", "atletismo", "maraton", "natacion",
    "olimpico", "olimpica", "medalla", "campeonato", "torneo", "competencia",
    "competicion", "deportista", "deportivo", "deportiva", "deportes",
)

PALABRAS_COMUNES = {
    "de", "del", "la", "las", "el", "los", "en", "un", "una", "y", "a", "al",
    "con", "por", "para", "ante", "tras", "que", "su", "sus", "se", "vs",
    "mexico", "deportes", "deportivo", "deportiva", "noticias", "hoy",
    "ninos", "ninas", "millones", "objetivo", "busca", "asi",
    "futbol", "partido", "liga", "equipo", "vence", "triunfo", "gana",
}


def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.casefold())
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn")


def tokens(texto):
    return {
        palabra for palabra in re.findall(r"[a-z0-9]+", normalizar(texto))
        if len(palabra) > 2 and palabra not in PALABRAS_COMUNES
    }


def es_deporte(titulo, descripcion):
    titulo_normal = normalizar(titulo)
    texto = normalizar(titulo + " " + descripcion)
    if any(palabra in texto for palabra in EXCLUIR):
        return False
    return any(palabra in titulo_normal for palabra in DEPORTES) or any(
        palabra in texto for palabra in ("campeonato", "seleccion", "atleta", "competencia")
    )


def titulo_limpio(titulo):
    """Quita el nombre del periódico al final del titular."""
    return titulo.rsplit(" - ", 1)[0]


def categoria(titulo):
    t = normalizar(titulo_limpio(titulo))
    if any(x in t for x in ("flag football", "tochito", "nfl", "dolphins", "super bowl")):
        return "americano"
    if any(x in t for x in ("futbol", "liga mx", "champions", "uefa", "pumas", "chivas", "cruz azul", "barcelona", "jamaica", "gignac", "memo ochoa")):
        return "futbol"
    if any(x in t for x in ("ciclismo", "ciclista", "yareli", "bicicleta")):
        return "ciclismo"
    if any(x in t for x in ("beisbol", "mlb", "dodgers", "yankees")):
        return "beisbol"
    if any(x in t for x in ("nba", "basquetbol")):
        return "basquetbol"
    if any(x in t for x in ("boxeo", "ufc", "mma")):
        return "combate"
    if any(x in t for x in ("formula 1", "formula uno", "gran premio", "automovilismo")):
        return "motor"
    if any(x in t for x in ("tenis", "atp", "wta")):
        return "tenis"
    return "otros"


def clave_evento(titulo):
    """Detecta coberturas de un mismo suceso con redacciones distintas."""
    t = normalizar(titulo_limpio(titulo))
    if "jamaica" in t and ("mexico" in t or "tricolor" in t):
        return "mexico-jamaica"
    if "4 millones" in t and any(x in t for x in ("nfl", "flag football", "tochito")):
        return "nfl-cuatro-millones"
    if "dolphins" in t and any(x in t for x in ("clinica", "flag football", "tochito")):
        return "dolphins-clinica"
    return None


def es_similar(titulo, elegidos):
    clave = clave_evento(titulo)
    actual = tokens(titulo_limpio(titulo))
    for elegido in elegidos:
        if clave and clave == clave_evento(elegido["titulo"]):
            return True
        previo = tokens(titulo_limpio(elegido["titulo"]))
        if actual and previo:
            interseccion = len(actual & previo)
            union = len(actual | previo)
            if interseccion >= 3 and interseccion / union >= 0.42:
                return True
    return False


def es_provisional(titulo):
    t = normalizar(titulo_limpio(titulo))
    return any(x in t for x in (
        "en vivo", "al medio tiempo", "medio tiempo", "minuto a minuto",
        "empata momentaneamente", "resultado parcial", "en directo",
    ))


def descargar():
    ahora = datetime.now(timezone.utc)
    limite = ahora - timedelta(hours=24)
    candidatos = []
    enlaces = set()
    fuentes_correctas = 0

    for medio, url in FUENTES.items():
        print("CONSULTANDO:", medio)
        try:
            solicitud = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(solicitud, timeout=20) as respuesta:
                contenido = respuesta.read()
            if not contenido:
                raise ValueError("La fuente devolvió una respuesta vacía")
            raiz = ET.fromstring(contenido)
            noticias = raiz.findall(".//channel/item")
            fuentes_correctas += 1
            for noticia in noticias:
                titulo = noticia.findtext("title", "").strip()
                fecha = noticia.findtext("pubDate", "").strip()
                enlace = noticia.findtext("link", "").strip()
                if not titulo or not enlace or enlace in enlaces:
                    continue
                try:
                    publicada = parsedate_to_datetime(fecha).astimezone(timezone.utc)
                except (ValueError, TypeError, AttributeError):
                    continue
                if not limite <= publicada <= ahora:
                    continue
                descripcion = noticia.findtext("description", "")
                if not es_deporte(titulo, descripcion) or es_provisional(titulo):
                    continue
                enlaces.add(enlace)
                candidatos.append({
                    "prioridad": 1,
                    "titulo": titulo,
                    "fecha": publicada.astimezone().strftime("%d/%m/%Y %H:%M"),
                    "fuente": medio,
                    "url": enlace,
                    "_publicada": publicada,
                })
        except Exception as error:
            print("ERROR EN", medio, ":", error)

    if fuentes_correctas == 0:
        raise SystemExit("ERROR: No se pudo consultar ninguna fuente deportiva.")

    candidatos.sort(key=lambda noticia: noticia["_publicada"], reverse=True)
    seleccion = []
    conteos = {}
    # Primera pasada: máximo tres noticias por disciplina.
    for noticia in candidatos:
        grupo = categoria(noticia["titulo"])
        if conteos.get(grupo, 0) >= 3 or es_similar(noticia["titulo"], seleccion):
            continue
        seleccion.append(noticia)
        conteos[grupo] = conteos.get(grupo, 0) + 1
        if len(seleccion) == 10:
            break

    # Si no hay suficientes disciplinas, completar sin repetir acontecimientos.
    if len(seleccion) < 10:
        for noticia in candidatos:
            if noticia in seleccion or es_similar(noticia["titulo"], seleccion):
                continue
            seleccion.append(noticia)
            if len(seleccion) == 10:
                break

    for noticia in seleccion:
        noticia.pop("_publicada")

    anteriores = {}
    if DESTINO.exists():
        try:
            for nota in json.loads(DESTINO.read_text(encoding="utf-8")):
                anteriores[nota["url"]] = nota.get("resumen", "")
        except (ValueError, KeyError, TypeError):
            print("AVISO: No se pudieron recuperar los resúmenes anteriores.")
    for nota in seleccion:
        nota["resumen"] = anteriores.get(nota["url"], "")

    # No publicar un archivo vacío que pueda dar lugar a un boletín sin noticias.
    if not seleccion:
        raise SystemExit("ERROR: No hay noticias deportivas recientes que cumplan los filtros.")

    DESTINO.write_text(json.dumps(seleccion, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DESCARGA DEPORTIVA FINALIZADA")
    print("NOTICIAS ENCONTRADAS:", len(seleccion))
    for noticia in seleccion:
        print("-", noticia["titulo"])


if __name__ == "__main__":
    descargar()
