"""Los ejemplos de SPEC.md §8 y sus copias en ejemplos/."""

import io
import re

import pytest

from cr7script.__main__ import main
from tests.ayuda import RAIZ, SPEC

EJEMPLOS = RAIZ / "ejemplos"


def bloques_de_la_spec():
    return re.findall(r"```\n(Calma, calma, estoy aquí\..*?)```", SPEC, re.S)


def test_los_archivos_coinciden_con_la_spec():
    hola, cuenta = bloques_de_la_spec()
    assert (EJEMPLOS / "hola_mundo.siu").read_text(encoding="utf-8") == hola
    assert (EJEMPLOS / "cuenta_atras.siu").read_text(encoding="utf-8") == cuenta


def ejecutar_ejemplo(nombre, entrada=b""):
    salida, errores = io.BytesIO(), io.BytesIO()
    codigo = main([str(EJEMPLOS / nombre)], io.BytesIO(entrada), salida, errores)
    assert errores.getvalue() == b""
    return codigo, salida.getvalue()


def test_hola_mundo():
    assert ejecutar_ejemplo("hola_mundo.siu") == (0, b"Hola, mundo!\n")


@pytest.mark.parametrize("entrada, esperado", [
    (b"3\n", b"3\n2\n1\n"),
    (b"1\n", b"1\n"),
    (b"0\n", b""),
])
def test_cuenta_atras(entrada, esperado):
    assert ejecutar_ejemplo("cuenta_atras.siu", entrada) == (0, esperado)
