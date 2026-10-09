"""La tabla de frases coincide con SPEC.md y cumple §2.2 y §2.4."""

import itertools
import re

import pytest

from cr7script.frases import FRASES, PATRON_FIN, Op, normalizar, reconocer
from tests.ayuda import seccion


def filas_tabla_3():
    texto = seccion("## 3. Tabla de comandos")
    return {int(n): frase for n, frase in re.findall(r"^\| (\d+) \| `([^`]+)` \|", texto, re.M)}


def formas_tabla_2_4():
    texto = seccion("### 2.4 Unicidad de las frases")
    return re.findall(r"^\| `([^`]+)` \| `([^`]+)`", texto, re.M)


def formas_normalizadas():
    """Forma normalizada de cada frase, como en §2.4 (fin mínimo, asignación sin «:»)."""
    return {op: normalizar(frase) for op, frase in FRASES.items()}


def test_la_tabla_tiene_los_17_comandos_de_la_spec():
    assert sorted(filas_tabla_3()) == list(range(1, 18))
    assert {op.value for op in Op} == set(range(1, 18))


@pytest.mark.parametrize("numero, frase", sorted(filas_tabla_3().items()))
def test_cada_frase_coincide_con_la_tabla_3(numero, frase):
    op = Op(numero)
    if op is Op.ASIGNAR:
        assert frase == FRASES[op] + ": <oración>"
    else:
        assert frase == FRASES[op]


def test_formas_normalizadas_coinciden_con_2_4():
    filas = formas_tabla_2_4()
    assert len(filas) == 17
    for frase, forma in filas:
        assert normalizar(frase.rstrip(":")) == forma


def test_ninguna_frase_es_prefijo_de_otra():
    formas = formas_normalizadas().values()
    for a, b in itertools.permutations(formas, 2):
        assert not b.startswith(a), (a, b)
        assert b.split()[:len(a.split())] != a.split(), (a, b)


def test_solo_el_fin_encaja_con_el_patron_de_fin():
    for op, forma in formas_normalizadas().items():
        assert bool(PATRON_FIN.fullmatch(forma)) == (op is Op.FIN)


def test_ninguna_frase_contiene_dos_puntos():
    assert all(":" not in frase for frase in FRASES.values())


@pytest.mark.parametrize("texto, esperado", [
    ("¡AGUA!", "agua"),
    ("eres de malaga quichiano QUICHIANO", "eres de malaga quichiano quichiano"),
    ("¿Eres de Málaga? Quichiano, quichiano", "eres de malaga quichiano quichiano"),
    ("  Más   un\tpoco\n y estás aquí ; madre mía hijo mío ", "mas un poco y estas aqui madre mia hijo mio"),
    ("Pingüino ñandú", "pinguino nandu"),
])
def test_normalizar(texto, esperado):
    assert normalizar(texto) == esperado


@pytest.mark.parametrize("texto, op", [
    ("siuuu", Op.FIN),
    ("siuuuuuuuu", Op.FIN),
    ("siuu", None),
    ("siu", None),
    ("agua", Op.AGUA),
    ("agua fria", None),
    ("calma calma estoy aqui", Op.INICIO),
])
def test_reconocer(texto, op):
    assert reconocer(texto) is op
