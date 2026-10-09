"""Asignación con «Ay mi madre, el Bicho: <oración>» (SPEC.md §4.2 y §2.5)."""

import re

import pytest

from tests.ayuda import AGUA, BICHO, MOSTRAR_NUMERO, correr, seccion


def ejemplos_4_2():
    texto = seccion("### 4.2 Ay mi madre, el Bicho")
    return re.findall(r"^\| `(Ay mi madre, el Bicho: [^`]+)` \| [^|]+ \| `(-?\d+)` \|", texto, re.M)


def test_la_tabla_4_2_tiene_8_ejemplos():
    assert len(ejemplos_4_2()) == 8


@pytest.mark.parametrize("jugada, valor", ejemplos_4_2())
def test_tabla_de_valores_4_2(jugada, valor):
    estado, _ = correr(jugada)
    assert estado.celda == int(valor)


@pytest.mark.parametrize("oracion, valor", [
    ("Turín", 5),                       # la tilde cuenta como una letra
    ("hat-trick", 8),                   # el guion no cuenta
    ("CR7 gol", 23),                    # los dígitos no cuentan
    ("¡ — 7 Siempre yo", 72),           # palabras sin letras: se ignoran
    ("Inigualable", 1),                 # 11 letras
    ("Futbolístico", 2),                # 12 letras
    ("Portuguesa Ronaldo", 7),          # ceros a la izquierda
    ("¡AUTOGOL, y", -1),                # autogol se reconoce normalizado
    ("y autogol", 17),                  # autogol solo cuenta al principio
    ("autogol autogol", -7),
    ("autogol Portuguesa", 0),
    ("Siempre\n   yo", 72),             # la oración puede ocupar varias líneas
    ("a:b", 2),                         # solo el primer «:» separa
    ("Siem(comentario)pre yo", 72),     # el comentario se elimina sin dejar hueco
    ("agua", 4),                        # §2.5: Agua no se activa en la oración
])
def test_valor_de_oraciones(oracion, valor):
    estado, _ = correr(f"{BICHO} {oracion}")
    assert estado.celda == valor


def test_la_asignacion_sustituye_el_valor():
    estado, _ = correr(f"{BICHO} Siempre yo", f"{BICHO} y")
    assert estado.celda == 1


def test_olvidar_el_punto_mezcla_agua_con_la_oracion():
    estado, _ = correr(f"{BICHO} Siempre yo\n{AGUA}")
    assert estado.celda == 724


def test_agua_en_su_propia_jugada_si_pone_a_cero():
    estado, _ = correr(f"{BICHO} Siempre yo", AGUA)
    assert estado.celda == 0


def test_precision_arbitraria():
    oracion = " ".join(["Siempre", "yo"] * 2500)  # 5000 cifras
    estado, salida = correr(f"{BICHO} {oracion}", MOSTRAR_NUMERO)
    assert salida == ("72" * 2500).encode()
    assert estado.celda == int("72" * 2500)
