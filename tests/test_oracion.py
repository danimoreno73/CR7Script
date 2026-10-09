"""Asignación con «Ay mi madre, el Bicho: <oración>» (SPEC.md §4.2 y §2.5)."""

import re

import pytest

from cr7script import ErrorAnalisis
from tests.ayuda import AGUA, BICHO, CHILENA, MOSTRAR_NUMERO, PENALTI, correr, seccion


def ejemplos_4_2():
    texto = seccion("### 4.2 Ay mi madre, el Bicho")
    return re.findall(r"^\| `(Ay mi madre, el Bicho: [^`]+)` \| [^|]+ \| `(-?\d+)` \|", texto, re.M)


def test_la_tabla_4_2_tiene_11_ejemplos():
    assert len(ejemplos_4_2()) == 11


@pytest.mark.parametrize("jugada, valor", ejemplos_4_2())
def test_tabla_de_valores_4_2(jugada, valor):
    estado, _ = correr(jugada)
    assert estado.celda == int(valor)


@pytest.mark.parametrize("oracion, valor", [
    ("7", 7),               # dorsal
    ("7 de", 72),
    ("CR7", 3),             # tres caracteres
    ("CR7 7", 37),
    ("cr7", 3),             # se compara normalizado
    ("¡CR7!", 3),
    ("7, Cristiano", 79),
    ("autogol 7", -7),
    ("autogol CR7", -3),
])
def test_casos_especiales(oracion, valor):
    estado, _ = correr(f"{BICHO} {oracion}")
    assert estado.celda == valor


@pytest.mark.parametrize("oracion, valor", [
    ("Turín", 5),
    ("TURIN", 5),                       # se compara normalizado
    ("¡Turín!", 5),
    ("Madridistas", 1),                 # 11 letras
    ("Futbolístico", 2),                # 12 letras
    ("Metropolitano", 3),               # 13 letras
    ("Portuguesa Ronaldo", 7),          # ceros a la izquierda
    ("Siuuu", 5),
    ("¡AUTOGOL, y", -1),                # autogol se reconoce normalizado
    ("¡ autogol y", -1),                # «¡» se ignora: autogol es la primera
    ("autogol Portuguesa", 0),
    ("¡ , Ronaldo yo !", 72),           # las palabras vacías se ignoran
    ("Ronaldo\n   yo", 72),             # la oración puede ocupar varias líneas
    ("Ronal(comentario)do yo", 72),     # el comentario se elimina sin dejar hueco
])
def test_valor_de_oraciones(oracion, valor):
    estado, _ = correr(f"{BICHO} {oracion}")
    assert estado.celda == valor


@pytest.mark.parametrize("oracion, palabra", [
    ("Siempre yo", "Siempre"),
    ("Ronaldo Siempre yo", "Siempre"),  # se informa de la primera
    ("agua", "agua"),                   # §2.5: Agua no se activa en la oración
    ("hat-trick", "hat-trick"),
    ("—", "—"),
    ("9", "9"),
    ("CR9", "CR9"),
    ("CR77", "CR77"),
    ("77", "77"),
    ("y autogol", "autogol"),           # autogol solo en primera posición
    ("autogol autogol", "autogol"),
    ("Siuuuu", "Siuuuu"),               # solo Siuuu, con cinco letras
    ("gol: gol", "gol:"),               # los dos puntos no se quitan al normalizar
    ("autogol —", "—"),                 # E09 antes que E02
])
def test_palabras_no_convocadas(oracion, palabra):
    with pytest.raises(ErrorAnalisis) as error:
        correr(f"{BICHO} {oracion}")
    assert error.value.codigo == "E09"
    assert error.value.detalle == f"«{palabra}» no está en la lista de convocados"


def test_la_asignacion_sustituye_el_valor():
    estado, _ = correr(f"{BICHO} Ronaldo yo", f"{BICHO} y")
    assert estado.celda == 1


def test_olvidar_el_punto_antes_de_agua_da_e09():
    with pytest.raises(ErrorAnalisis) as error:
        correr(f"{BICHO} Ronaldo yo\n{AGUA}")
    assert error.value.codigo == "E09"


@pytest.mark.parametrize("jugada, valor", [(CHILENA, 72725), (PENALTI, 7227242)])
def test_frases_que_se_suman_en_silencio_si_falta_el_punto(jugada, valor):
    # §2.5: estas frases solo tienen palabras convocadas.
    estado, _ = correr(f"{BICHO} Ronaldo yo\n{jugada}")
    assert estado.celda == valor


def test_agua_en_su_propia_jugada_si_pone_a_cero():
    estado, _ = correr(f"{BICHO} Ronaldo yo", AGUA)
    assert estado.celda == 0


def test_precision_arbitraria():
    oracion = " ".join(["Ronaldo", "yo"] * 2500)  # 5000 cifras
    estado, salida = correr(f"{BICHO} {oracion}", MOSTRAR_NUMERO)
    assert salida == ("72" * 2500).encode()
    assert estado.celda == int("72" * 2500)
