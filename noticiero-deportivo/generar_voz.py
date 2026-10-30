
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

    for intento in range(1, 4):
        try:
            print(f"INTENTO {intento} DE 3")

            archivo_temporal.unlink(missing_ok=True)

            comunicacion = edge_tts.Communicate(
                texto,
                VOZ,
                rate="+15%"
            )

            await comunicacion.save(str(archivo_temporal))

            if not archivo_temporal.exists():
                raise RuntimeError("No se generó el archivo de audio.")

            if archivo_temporal.stat().st_size < 1000:
                raise RuntimeError("El audio generado está incompleto.")

            archivo_temporal.replace(AUDIO)

            print("VOZ DEPORTIVA GENERADA CORRECTAMENTE")
            print("Archivo:", AUDIO)
            return

        except Exception as error:
            print(f"ERROR EN INTENTO {intento}: {error}")

            archivo_temporal.unlink(missing_ok=True)

            if intento == 3:
                raise RuntimeError(
                    "No se pudo generar la voz después de 3 intentos."
                ) from error

            print("ESPERANDO 15 SEGUNDOS...")
            await asyncio.sleep(15)

asyncio.run(generar())
