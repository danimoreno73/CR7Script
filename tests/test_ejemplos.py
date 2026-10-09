"""Los programas de ejemplos/, incluidos los de SPEC.md §8."""

import io
import re
import subprocess
import sys

import pytest

from cr7script.__main__ import main
from cr7script.frases import Op, normalizar
from cr7script.parser import analizar
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


@pytest.mark.parametrize("entrada, esperado", [
    (b"3\n4\n", b"7\n"),
    (b"-10\n4\n", b"-6\n"),
    (b"0\n0\n", b"0\n"),
    (b"123456789123456789\n1\n", b"123456789123456790\n"),
])
def test_sumar(entrada, esperado):
    assert ejecutar_ejemplo("sumar.siu", entrada) == (0, esperado)


@pytest.mark.parametrize("entrada, esperado", [
    (b"Hola, mundo!\n", b"Hola, mundo!\n"),
    ("¡Siuuu! ñ 😀".encode(), "¡Siuuu! ñ 😀".encode()),
    (b"", b""),
    (b"ab\x00cd", b"ab"),   # un carácter 0 se confunde con el fin de la entrada
])
def test_eco(entrada, esperado):
    assert ejecutar_ejemplo("eco.siu", entrada) == (0, esperado)


@pytest.mark.parametrize("entrada, esperado", [
    (b"10\n", b"0\n1\n1\n2\n3\n5\n8\n13\n21\n34\n"),
    (b"1\n", b"0\n"),
    (b"2\n", b"0\n1\n"),
    (b"0\n", b""),
])
def test_fibonacci(entrada, esperado):
    assert ejecutar_ejemplo("fibonacci.siu", entrada) == (0, esperado)


@pytest.mark.parametrize("nombre", ["cuenta_atras.siu", "fibonacci.siu"])
@pytest.mark.parametrize("entrada", [b"-1\n", b"-5\n", b"-123456789\n"])
def test_entrada_negativa_no_escribe_nada_y_termina(nombre, entrada):
    # En un proceso aparte, para que un bucle infinito falle por tiempo y no
    # cuelgue el resto de tests.
    resultado = subprocess.run(
        [sys.executable, "-m", "cr7script", str(EJEMPLOS / nombre)],
        input=entrada, capture_output=True, timeout=30, cwd=RAIZ,
    )
    assert (resultado.returncode, resultado.stdout, resultado.stderr) == (0, b"", b"")


def test_fibonacci_con_precision_arbitraria():
    _, salida = ejecutar_ejemplo("fibonacci.siu", b"300\n")
    terminos = salida.decode().split("\n")
    assert terminos[299] == "137347080577163115432025771710279131845700275212767467264610201"


@pytest.mark.parametrize("archivo", sorted(EJEMPLOS.glob("*.siu")), ids=lambda p: p.name)
def test_los_ejemplos_no_tienen_comentarios(archivo):
    texto = archivo.read_text(encoding="utf-8")
    assert "(" not in texto and ")" not in texto


def test_los_ejemplos_usan_las_mecanicas_propias():
    usadas = {
        ins.op
        for archivo in EJEMPLOS.glob("*.siu")
        for ins in analizar(archivo.read_text(encoding="utf-8")).instrucciones
    }
    assert {Op.CHILENA, Op.SUMAR, Op.PENALTI} <= usadas


def test_algun_ejemplo_usa_los_casos_especiales():
    palabras = {
        normalizar(palabra)
        for archivo in EJEMPLOS.glob("*.siu")
        for linea in archivo.read_text(encoding="utf-8").splitlines()
        if linea.startswith("Ay mi madre, el Bicho:")
        for palabra in linea.split(":", 1)[1].rstrip(".").split()
    }
    assert {"7", "cr7"} <= palabras
