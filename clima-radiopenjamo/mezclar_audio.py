
import subprocess
from pathlib import Path

# RADIO PENJAMO - MEZCLADOR DEL CLIMA

CARPETA = Path(__file__).resolve().parent

VOZ = CARPETA / "noticiero-clima.mp3"

MUSICA = CARPETA / (
    "alex-morgan-news-intro-headline-"
    "broadcast-open-575875.mp3"
)

SALIDA = CARPETA / "noticiero-clima-final.mp3"


def duracion(archivo):
    resultado = subprocess.check_output([
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(archivo)
    ])
    return float(resultado.decode().strip())


def mezclar():
    if not VOZ.is_file():
        raise SystemExit("ERROR: Falta el audio de Dalia.")

    if not MUSICA.is_file():
        raise SystemExit("ERROR: Falta la cortinilla musical.")

    duracion_voz = duracion(VOZ)
    duracion_total = duracion_voz + 12

    print("INICIANDO MEZCLA MUSICAL...", flush=True)

    # Entrada de 6 segundos, voz y cierre musical.
    # La cortinilla se repite a volumen bajo.
    filtro = (
        "[0:a]asetpts=PTS-STARTPTS,"
        "adelay=6000:all=1,"
        "volume=1.0[voz];"

        "[1:a]aloop=loop=-1:size=2147483647,"
        f"atrim=duration={duracion_total},"
        "asetpts=PTS-STARTPTS,"
        "volume=0.12[musica];"

        "[voz][musica]amix=inputs=2:"
        "duration=longest:normalize=0,"
        f"afade=t=out:st={duracion_total-3}:d=3"
        "[final]"
    )

    comando = [
        "ffmpeg",
        "-y",
        "-i", str(VOZ),
        "-i", str(MUSICA),
        "-filter_complex", filtro,
        "-map", "[final]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(SALIDA)
    ]

    subprocess.run(comando, check=True)

    if not SALIDA.is_file() or SALIDA.stat().st_size == 0:
        raise SystemExit("ERROR: No se genero el MP3 final.")

    print("MEZCLA MUSICAL TERMINADA CORRECTAMENTE")
    print(f"Archivo: {SALIDA}")


if __name__ == "__main__":
    mezclar()

