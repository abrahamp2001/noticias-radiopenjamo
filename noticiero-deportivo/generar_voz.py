import asyncio
from pathlib import Path
import edge_tts

CARPETA = Path(__file__).resolve().parent
GUION = CARPETA / "guion_deportivo.txt"
AUDIO = CARPETA / "voz-deportiva.mp3"

VOZ = "es-MX-JorgeNeural"

async def generar():
    if not GUION.exists():
        raise SystemExit("ERROR: No existe el guion deportivo.")

    texto = GUION.read_text(encoding="utf-8").strip()

    if not texto:
        raise SystemExit("ERROR: El guion está vacío.")

    print("GENERANDO VOZ DEL NOTICIERO DEPORTIVO...")

    archivo_temporal = AUDIO.with_suffix(".temporal.mp3")

    try:
        comunicacion = edge_tts.Communicate(
            texto,
            VOZ,
            rate="+15%"
        )
        await comunicacion.save(str(archivo_temporal))

        if archivo_temporal.stat().st_size < 1000:
            raise RuntimeError("El audio generado está incompleto.")

        archivo_temporal.replace(AUDIO)
    finally:
        archivo_temporal.unlink(missing_ok=True)

    print("VOZ DEPORTIVA GENERADA CORRECTAMENTE")
    print("Archivo:", AUDIO)

asyncio.run(generar())
