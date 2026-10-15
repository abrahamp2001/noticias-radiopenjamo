import subprocess
from pathlib import Path

carpeta = Path(__file__).resolve().parent
voz = carpeta / "noticiero-regional.mp3"
cortinilla = carpeta / "cortinilla_noticias.mp3"
musica = carpeta / "musica_fondo.mp3"
final = carpeta / "noticiero-regional-final.mp3"
temporal = carpeta / "noticiero-regional-final.tmp.mp3"

if not all(p.exists() for p in (voz, cortinilla, musica)):
    raise SystemExit("ERROR: Falta la voz, la cortinilla o la musica.")

filtros = (
    "[0:a]aresample=44100,atrim=0:8,asetpts=PTS-STARTPTS[entrada];"
    "[1:a]aresample=44100,asetpts=PTS-STARTPTS[voz];"
    "[2:a]aresample=44100,volume=0.10,asetpts=PTS-STARTPTS[musica];"
    "[voz][musica]amix=inputs=2:duration=first:"
    "dropout_transition=0:normalize=0[noticias];"
    "[0:a]aresample=44100,atrim=0:8,asetpts=PTS-STARTPTS[salida];"
    "[entrada][noticias][salida]concat=n=3:v=0:a=1[out]"
)

subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error",
    "-i", str(cortinilla),
    "-i", str(voz),
    "-stream_loop", "-1", "-i", str(musica),
    "-filter_complex", filtros,
    "-map", "[out]",
    "-codec:a", "libmp3lame",
    "-b:a", "192k",
    str(temporal)
], check=True)

if temporal.stat().st_size < 1000:
    raise SystemExit("ERROR: El audio final esta incompleto.")

temporal.replace(final)
print("NOTICIERO REGIONAL CON MUSICA PREPARADO CORRECTAMENTE")
