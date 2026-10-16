
import asyncio
from pathlib import Path
import edge_tts

CARPETA = Path(__file__).resolve().parent
GUION = CARPETA / "guion_clima.txt"
AUDIO = CARPETA / "noticiero-clima.mp3"

VOZ = "es-MX-DaliaNeural"

async def generar():
    if not GUION.exists():
        raise SystemExit("ERROR: No existe el guion del clima.")

    texto = GUION.read_text(encoding="utf-8").strip()

    if not texto:
        raise SystemExit("ERROR: El guion del clima esta vacio.")

    print("GENERANDO VOZ DEL NOTICIERO DEL CLIMA...")

    temporal = CARPETA / "clima-temporal.mp3"

    try:
        comunicacion = edge_tts.Communicate(
            texto,
            VOZ,
            rate="+15%"
        )

        await comunicacion.save(str(temporal))
        temporal.replace(AUDIO)

        print("NOTICIERO DEL CLIMA GENERADO CORRECTAMENTE")
        print(f"Archivo: {AUDIO}")

    finally:
        if temporal.exists():
            temporal.unlink()

if __name__ == "__main__":
    asyncio.run(generar())

