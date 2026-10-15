import asyncio
from pathlib import Path
import edge_tts

CARPETA = Path(__file__).resolve().parent
GUION = CARPETA / "guion_espectaculos.txt"
AUDIO = CARPETA / "noticiero-espectaculos.mp3"

VOZ = "es-CO-SalomeNeural"

async def generar():
    if not GUION.exists():
        raise SystemExit("ERROR: No existe el guion regional.")

    texto = GUION.read_text(encoding="utf-8").strip()

    if not texto:
        raise SystemExit("ERROR: El guion está vacío.")

    print("GENERANDO VOZ DEL PROGRAMA DE ESPECTACULOS...")

    archivo_temporal = AUDIO.with_suffix(".temporal.mp3")

    try:
        comunicacion = edge_tts.Communicate(
            texto,
            VOZ,
            rate="+30%"
        )
        await comunicacion.save(str(archivo_temporal))

        if archivo_temporal.stat().st_size < 1000:
            raise RuntimeError("El audio generado está incompleto.")

        archivo_temporal.replace(AUDIO)
    finally:
        archivo_temporal.unlink(missing_ok=True)

    print("VOZ DE SALOME GENERADA CORRECTAMENTE")
    print("Archivo:", AUDIO)

asyncio.run(generar())
