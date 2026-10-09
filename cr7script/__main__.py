"""Uso: python -m cr7script archivo.siu"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import BinaryIO

from .errores import ErrorAnalisis, ErrorEjecucion
from .interprete import ejecutar
from .parser import analizar

SALIDA_OK = 0
SALIDA_ANALISIS = 1
SALIDA_EJECUCION = 2
SALIDA_USO = 3  # §6.3: argumentos incorrectos o archivo ilegible


def main(argv: list[str] | None = None, entrada: BinaryIO | None = None,
         salida: BinaryIO | None = None, errores: BinaryIO | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    entrada = sys.stdin.buffer if entrada is None else entrada
    salida = sys.stdout.buffer if salida is None else salida
    errores = sys.stderr.buffer if errores is None else errores

    def avisar(mensaje: str) -> None:
        salida.flush()
        errores.write((mensaje + "\n").encode("utf-8"))
        errores.flush()

    if len(argv) != 1:
        avisar("uso: python -m cr7script archivo.siu")
        return SALIDA_USO

    ruta = argv[0]
    try:
        fuente = Path(ruta).read_bytes().decode("utf-8")
    except OSError as e:
        avisar(f"CR7Script: no se puede leer «{ruta}»: {e.strerror or e}")
        return SALIDA_USO
    except UnicodeDecodeError:
        avisar(f"CR7Script: no se puede leer «{ruta}»: no es UTF-8 válido")
        return SALIDA_USO

    try:
        programa = analizar(fuente)
    except ErrorAnalisis as e:
        avisar(e.mensaje())
        return SALIDA_ANALISIS

    try:
        ejecutar(programa, entrada, salida)
    except ErrorEjecucion as e:
        avisar(e.mensaje())
        return SALIDA_EJECUCION
    finally:
        salida.flush()
    return SALIDA_OK


if __name__ == "__main__":
    sys.exit(main())
