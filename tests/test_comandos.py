"""Un test (o más) por cada comando de SPEC.md §3."""

import io

import pytest

from cr7script import ErrorEjecucion, analizar, ejecutar
from tests.ayuda import (
    AGUA, BICHO, CHILENA, COPIAR, DERECHA, FIN, INICIO, IZQUIERDA, LEER_CARACTER,
    LEER_NUMERO, MOSTRAR_CARACTER, MOSTRAR_NUMERO, PEGAR, PENALTI, SUMAR,
    asignar, correr,
)


# 1 y 2: inicio y fin

def test_programa_minimo_no_escribe_nada():
    estado, salida = correr()
    assert salida == b""
    assert (estado.campo, estado.posicion, estado.portapapeles) == ([0], 0, 0)


@pytest.mark.parametrize("fin", ["¡Siuuu!", "¡SIUUUUUUU!", "siuuuu", "¡Siuuu!.", "¡Siuuu!..."])
def test_variantes_del_fin(fin):
    programa = analizar(f"{INICIO}.\n{fin}")
    ejecutar(programa, io.BytesIO(), io.BytesIO())


def test_frases_sin_distinguir_mayusculas_tildes_ni_signos():
    fuente = "¡CALMA,   calma, estoy AQUI!.\nay MI madre el bicho: Siempre yo.\nsoy el primero el segundo y el tercero.\nsiuuu"
    salida = io.BytesIO()
    ejecutar(analizar(fuente), io.BytesIO(), salida)
    assert salida.getvalue() == b"72"


def test_jugada_en_varias_lineas_y_comentarios():
    fuente = f"{INICIO}. (comentario. con. puntos)\nSoy el primero,\n  el segundo\n  y el tercero.\n{FIN}"
    salida = io.BytesIO()
    ejecutar(analizar(fuente), io.BytesIO(), salida)
    assert salida.getvalue() == b"0"


# 3 y 4: movimiento

def test_derecha_amplia_el_campo_con_ceros():
    estado, _ = correr(DERECHA, DERECHA)
    assert estado.campo == [0, 0, 0]
    assert estado.posicion == 2


def test_izquierda_vuelve_a_la_celda_anterior():
    estado, _ = correr(asignar(5), DERECHA, asignar(7), IZQUIERDA)
    assert estado.posicion == 0
    assert estado.campo == [5, 7]
    assert estado.celda == 5


# 5: asignar (más casos en test_oracion.py)

def test_asignar_pone_el_valor_en_la_celda_actual():
    estado, _ = correr(DERECHA, f"{BICHO} Cristiano Ronaldo")
    assert estado.campo == [0, 97]


# 6: agua

def test_agua_pone_a_cero_y_no_toca_el_portapapeles():
    estado, _ = correr(asignar(9), COPIAR, AGUA)
    assert estado.celda == 0
    assert estado.portapapeles == 9


# 7: mostrar número

@pytest.mark.parametrize("valor, texto", [(0, b"0"), (97, b"97"), (-15, b"-15")])
def test_mostrar_numero(valor, texto):
    _, salida = correr(asignar(valor), MOSTRAR_NUMERO)
    assert salida == texto


def test_mostrar_numero_no_anade_separadores():
    _, salida = correr(asignar(1), MOSTRAR_NUMERO, asignar(2), MOSTRAR_NUMERO)
    assert salida == b"12"


# 8: mostrar carácter

@pytest.mark.parametrize("valor, esperado", [
    (72, b"H"),
    (10, b"\n"),
    (0, b"\x00"),
    (241, "ñ".encode()),
    (0x10FFFF, chr(0x10FFFF).encode()),
])
def test_mostrar_caracter_en_utf8(valor, esperado):
    _, salida = correr(asignar(valor), MOSTRAR_CARACTER)
    assert salida == esperado


# 9: leer número

@pytest.mark.parametrize("entrada, valor", [
    (b"42\n", 42),
    (b"  -7  \n", -7),
    (b"+5\n", 5),
    (b"0012\n", 12),
    (b"33", 33),          # última línea sin salto final
    (b"8\r\n", 8),        # el \r es un espacio del extremo
    (b"9" * 5000 + b"\n", int("9" * 5000)),
])
def test_leer_numero(entrada, valor):
    estado, _ = correr(LEER_NUMERO, entrada=entrada)
    assert estado.celda == valor


def test_leer_numero_consume_la_linea_entera():
    estado, _ = correr(LEER_NUMERO, DERECHA, LEER_NUMERO, entrada=b"1\n2\n")
    assert estado.campo == [1, 2]


# 10: leer carácter

@pytest.mark.parametrize("entrada, valor", [
    (b"a", 97),
    ("ñ".encode(), 241),
    ("😀".encode(), 0x1F600),
    (b"\n", 10),
    (b"", 0),              # EOF: guarda 0 y no es error
])
def test_leer_caracter(entrada, valor):
    estado, _ = correr(asignar(5), LEER_CARACTER, entrada=entrada)
    assert estado.celda == valor


def test_leer_caracter_lee_de_uno_en_uno():
    estado, _ = correr(LEER_CARACTER, DERECHA, LEER_CARACTER, DERECHA, LEER_CARACTER,
                       entrada="añ".encode())
    assert estado.campo == [97, 241, 0]


def test_leer_numero_y_caracter_comparten_la_entrada():
    estado, _ = correr(LEER_NUMERO, DERECHA, LEER_CARACTER, entrada=b"12\nx")
    assert estado.campo == [12, ord("x")]


# 13 y 14: copiar y pegar

def test_copiar_no_cambia_la_celda():
    estado, _ = correr(asignar(33), COPIAR)
    assert (estado.celda, estado.portapapeles) == (33, 33)


def test_pegar_copia_el_portapapeles_en_otra_celda():
    estado, _ = correr(asignar(33), COPIAR, DERECHA, PEGAR)
    assert estado.campo == [33, 33]
    assert estado.portapapeles == 33


# 15: chilena

def test_chilena_intercambia_celda_y_portapapeles():
    estado, _ = correr(asignar(9), COPIAR, asignar(5), CHILENA)
    assert (estado.celda, estado.portapapeles) == (9, 5)


# 16: losh dosh

def test_losh_dosh_suma_el_portapapeles():
    estado, _ = correr(asignar(-1), COPIAR, asignar(72), SUMAR)
    assert (estado.celda, estado.portapapeles) == (71, -1)


# 17: penalti (más casos con bucles en test_bucles.py)

def test_penalti_fallado_salta_la_jugada_siguiente():
    _, salida = correr(PENALTI, asignar(7), MOSTRAR_NUMERO)
    assert salida == b"0"


def test_penalti_marcado_sigue_con_normalidad():
    _, salida = correr(asignar(1), PENALTI, asignar(7), MOSTRAR_NUMERO)
    assert salida == b"7"


def test_penaltis_seguidos_solo_saltan_uno():
    # El primero falla y se salta el segundo; la asignación sí se ejecuta.
    _, salida = correr(PENALTI, PENALTI, asignar(7), MOSTRAR_NUMERO)
    assert salida == b"7"


def test_penalti_que_salta_el_fin_termina_igual():
    _, salida = correr(MOSTRAR_NUMERO, PENALTI)
    assert salida == b"0"


def test_errores_de_ejecucion_son_excepciones():
    with pytest.raises(ErrorEjecucion):
        correr(IZQUIERDA)
