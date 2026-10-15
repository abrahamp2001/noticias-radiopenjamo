from pathlib import Path
import subprocess

carpeta = Path(__file__).resolve().parent
voz = carpeta / "noticiero-espectaculos.mp3"
musica = carpeta / "musica_fondo.mp3"
salida = carpeta / "espectaculos-con-musica.mp3"
temporal = carpeta / "mezcla-temporal.mp3"

if not voz.exists() or not musica.exists():
    raise SystemExit("ERROR: falta la voz o la musica.")

comando = [
    "ffmpeg", "-y",
    "-stream_loop", "-1",
    "-i", str(musica),
    "-i", str(voz),
    "-filter_complex",
    "[0:a]volume=0.12[m];"
    "[m][1:a]amix=inputs=2:duration=shortest:"
    "dropout_transition=0:normalize=0[a]",
    "-map", "[a]",
    "-c:a", "libmp3lame",
    "-b:a", "192k",
    str(temporal)
]

subprocess.run(comando, check=True)

if temporal.stat().st_size < 1000:
    raise RuntimeError("La mezcla esta incompleta.")

temporal.replace(salida)
print("MEZCLA AUTOMATICA GENERADA CORRECTAMENTE")
print("ARCHIVO:", salida)
