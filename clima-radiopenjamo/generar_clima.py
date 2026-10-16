
import asyncio
import re
from pathlib import Path
import edge_tts

CARPETA = Path(__file__).resolve().parent
GUION = CARPETA / "guion_clima.txt"
AUDIO = CARPETA / "noticiero-clima.mp3"

VOZ = "es-MX-DaliaNeural"

async def generar():
    if not GUION.exists():
        raise SystemExit("ERROR: No existe el guion.")

    texto = GUION.read_text(
        encoding="utf-8"
    ).strip()

    if not texto:
        raise SystemExit("ERROR: Guion vacio.")

    # Unificar espacios y saltos de linea
    texto = re.sub(r"\s+", " ", texto)

    # Sustituir pausas de comas por espacios
    texto = re.sub(r",\s*", " ", texto)

    # Reducir pausas de puntos intermedios
    texto = re.sub(
        r"\.(?=\s+\S)",
        ",",
        texto
    )

    # Limpiar espacios duplicados
    texto = re.sub(r"\s+", " ", texto).strip()

    print("GENERANDO LOCUCION CONTINUA...")

    temporal = CARPETA / "voz-temporal.mp3"

    try:
        comunicacion = edge_tts.Communicate(
            text=texto,
            voice=VOZ,
            rate="+8%",
            pitch="+0Hz"
        )

        await comunicacion.save(str(temporal))
        temporal.replace(AUDIO)

        print("LOCUCION GENERADA CORRECTAMENTE")
        print(f"Archivo: {AUDIO}")

    finally:
        if temporal.exists():
            temporal.unlink()

if __name__ == "__main__":
    asyncio.run(generar())
