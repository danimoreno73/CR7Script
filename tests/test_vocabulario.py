"""El vocabulario de cr7script/vocabulario.py coincide con el Anexo A de SPEC.md."""

import itertools
import re

import pytest

from cr7script.frases import normalizar
from cr7script.vocabulario import (
    AUTOGOL, CONECTORES, ESPECIALES, TEMATICAS, cifra, contar_letras,
)
from tests.ayuda import SPEC


def anexo():
    return SPEC[SPEC.index("## Anexo A. Vocabulario de la oración"):]


def tabla_del_anexo():
    """{cifra: (conectores, temáticas)} tal como aparece en el Anexo A."""
    filas = re.findall(r"^\| (\d) \| [^|]+ \| ([^|]+) \| ([^|]+) \|$", anexo(), re.M)

    def palabras(celda):
        celda = celda.strip()
        return () if celda == "—" else tuple(p.strip() for p in celda.split(","))

    return {int(c): (palabras(con), palabras(tem)) for c, con, tem in filas}


def todas_las_palabras():
    return [(c, p) for grupo in (CONECTORES, TEMATICAS) for c, ps in grupo.items() for p in ps]


def test_el_anexo_coincide_con_vocabulario_py():
    tabla = tabla_del_anexo()
    assert sorted(tabla) == list(range(10))
    for c, (conectores, tematicas) in tabla.items():
        assert conectores == CONECTORES.get(c, ()), c
        assert tematicas == TEMATICAS[c], c


def test_los_casos_especiales_coinciden_con_el_anexo():
    filas = re.findall(r"^\| `([^`]+)` \| (\d) \|", anexo(), re.M)
    assert {token: int(c) for token, c in filas} == ESPECIALES == {"7": 7, "CR7": 3}


def test_las_diez_cifras_tienen_al_menos_cinco_palabras():
    por_cifra = {c: 0 for c in range(10)}
    for c, _ in todas_las_palabras():
        por_cifra[c] += 1
    assert all(n >= 5 for n in por_cifra.values()), por_cifra


@pytest.mark.parametrize("c, palabra", todas_las_palabras())
def test_cada_palabra_aporta_sus_letras_modulo_10(c, palabra):
    assert contar_letras(palabra) % 10 == c
    assert contar_letras(normalizar(palabra)) == contar_letras(palabra)
    assert cifra(normalizar(palabra)) == c


def test_no_hay_palabras_repetidas_al_normalizar():
    normalizadas = [normalizar(p) for _, p in todas_las_palabras()] + [normalizar(t) for t in ESPECIALES]
    assert len(normalizadas) == len(set(normalizadas))


def test_autogol_no_es_una_palabra_del_vocabulario():
    assert cifra(AUTOGOL) is None


def test_solo_los_casos_especiales_tienen_digitos_o_les_faltan_letras():
    for _, palabra in todas_las_palabras():
        assert palabra.isalpha(), palabra


def test_conectores_cubren_las_cifras_uno_y_dos():
    assert len(CONECTORES[1]) >= 4 and len(CONECTORES[2]) >= 4
    assert all(p.islower() for p in itertools.chain(*CONECTORES.values()))
