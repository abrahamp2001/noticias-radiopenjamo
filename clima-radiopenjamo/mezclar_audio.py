
import subprocess
from pathlib import Path
import imageio_ffmpeg

# RADIO PENJAMO - MEZCLADOR DEL CLIMA

CARPETA = Path(__file__).resolve().parent

VOZ = CARPETA / "noticiero-clima.mp3"

MUSICA = CARPETA / (
    "alex-morgan-news-intro-headline-"
    "broadcast-open-575875.mp3"
)

SALIDA = CARPETA / "noticiero-clima-final.mp3"

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def duracion(archivo):
    comando = [
        FFMPEG,
        "-hide_banner",
        "-i", str(archivo),
        "-f", "null",
        "-"
    ]

    resultado = subprocess.run(
        comando,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    import re

    tiempos = re.findall(
        r"time=(\d+):(\d+):(\d+(?:\.\d+)?)",
        resultado.stderr
    )

    if not tiempos:
        raise RuntimeError(
            f"No se pudo calcular la duracion de {archivo}"
        )

    horas, minutos, segundos = tiempos[-1]

    return (
        int(horas) * 3600
        + int(minutos) * 60
        + float(segundos)
    )


def mezclar():
    if not VOZ.is_file():
        raise SystemExit("ERROR: Falta el audio de Dalia.")

    if not MUSICA.is_file():
        raise SystemExit("ERROR: Falta la cortinilla musical.")

    duracion_voz = duracion(VOZ)
    duracion_total = duracion_voz + 12

    print("INICIANDO MEZCLA MUSICAL...", flush=True)

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
        FFMPEG,
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
