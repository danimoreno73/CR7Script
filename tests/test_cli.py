"""Línea de órdenes: python -m cr7script archivo.siu (SPEC.md §6.3)."""

import io
import subprocess
import sys

from cr7script.__main__ import main
from tests.ayuda import RAIZ, lanzar, programa

USO = "uso: python -m cr7script archivo.siu\n"


def lanzar_con_argumentos(argv):
    salida, errores = io.BytesIO(), io.BytesIO()
    codigo = main(argv, io.BytesIO(), salida, errores)
    return codigo, salida.getvalue(), errores.getvalue().decode("utf-8")


def test_sin_argumentos():
    assert lanzar_con_argumentos([]) == (3, b"", USO)


def test_demasiados_argumentos():
    assert lanzar_con_argumentos(["a.siu", "b.siu"]) == (3, b"", USO)


def test_archivo_inexistente(tmp_path):
    ruta = tmp_path / "no_existe.siu"
    codigo, salida, errores = lanzar_con_argumentos([str(ruta)])
    assert (codigo, salida) == (3, b"")
    assert errores.startswith(f"CR7Script: no se puede leer «{ruta}»: ")


def test_fuente_que_no_es_utf8(tmp_path):
    codigo, salida, errores = lanzar(tmp_path, b"Calma, calma, estoy aqu\xed.\n\xa1Siuuu!")
    assert (codigo, salida) == (3, b"")
    assert errores == f"CR7Script: no se puede leer «{tmp_path / 'programa.siu'}»: no es UTF-8 válido\n"


def test_bom_al_principio_se_ignora(tmp_path):
    fuente = "﻿" + programa("Ay mi madre, el Bicho: Ronaldo yo", "Soy el primero, el segundo y el tercero")
    assert lanzar(tmp_path, fuente) == (0, b"72", "")


def test_bom_no_cambia_las_lineas(tmp_path):
    codigo, _, errores = lanzar(tmp_path, "﻿" + programa("Pase de Benzema"))
    assert codigo == 1
    assert errores.startswith("CR7Script: E01 Fuera de juego (jugada 2, línea 2): ")


def test_programa_correcto_sale_con_cero(tmp_path):
    assert lanzar(tmp_path, programa()) == (0, b"", "")


def test_modulo_ejecutable():
    resultado = subprocess.run(
        [sys.executable, "-m", "cr7script", "ejemplos/hola_mundo.siu"],
        cwd=RAIZ, capture_output=True, timeout=30,
    )
    assert resultado.returncode == 0
    assert resultado.stdout == b"Hola, mundo!\n"  # sin traducir \n a \r\n
    assert resultado.stderr == b""


def test_modulo_ejecutable_con_error(tmp_path):
    archivo = tmp_path / "error.siu"
    archivo.write_text(programa("He vuelto a casa"), encoding="utf-8")
    resultado = subprocess.run(
        [sys.executable, "-m", "cr7script", str(archivo)],
        cwd=RAIZ, capture_output=True, timeout=30,
    )
    assert resultado.returncode == 2
    assert resultado.stderr.decode("utf-8").startswith("CR7Script: E10 Balón fuera (jugada 2, línea 2): ")
