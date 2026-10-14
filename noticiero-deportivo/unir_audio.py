import subprocess
from pathlib import Path

carpeta = Path(__file__).resolve().parent
voz = carpeta / "voz-deportiva.mp3"
cortinilla = carpeta / "cortinilla_deportiva.mp3"
final = carpeta / "noticiero-deportivo.mp3"
temporal = carpeta / "noticiero-deportivo.tmp.mp3"

if not voz.exists() or not cortinilla.exists():
    raise SystemExit("ERROR: Falta la voz o la cortinilla.")

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error",
    "-i", str(cortinilla),
    "-i", str(voz),
    "-filter_complex",
    "[0:a]aresample=44100,atrim=0:8,asetpts=PTS-STARTPTS[a];"
    "[1:a]aresample=44100,asetpts=PTS-STARTPTS[b];"
    "[0:a]aresample=44100,atrim=0:8,asetpts=PTS-STARTPTS[c];"
    "[a][b][c]concat=n=3:v=0:a=1[out]",
    "-map", "[out]",
    "-codec:a", "libmp3lame",
    "-b:a", "192k",
    str(temporal)
], check=True)

if temporal.stat().st_size < 1000:
    raise SystemExit("ERROR: El audio final está incompleto.")

temporal.replace(final)
print("NOTICIERO CON CORTINILLAS PREPARADO CORRECTAMENTE")
