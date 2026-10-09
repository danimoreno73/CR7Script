"""Errores E01–E12 (SPEC.md §6): código, mensaje, posición y código de salida."""

import pytest

from tests.ayuda import (
    ABRIR, AGUA, CERRAR, IZQUIERDA, LEER_CARACTER, LEER_NUMERO, MOSTRAR_CARACTER,
    MOSTRAR_NUMERO, asignar, lanzar, programa,
)

CALMA = "Calma, calma, estoy aquí"
SIUUU = "¡Siuuu!"
TEXTO_E06 = "este «Yo no persigo los récords» no tiene su «Los récords me persiguen a mí»"
TEXTO_E07 = "este «Los récords me persiguen a mí» no tiene ningún «Yo no persigo los récords» abierto"


def error_de_analisis(tmp_path, fuente):
    codigo, salida, errores = lanzar(tmp_path, fuente)
    assert codigo == 1
    assert salida == b""
    return errores


def error_de_ejecucion(tmp_path, fuente, entrada=b""):
    codigo, salida, errores = lanzar(tmp_path, fuente, entrada)
    assert codigo == 2
    return salida, errores


# E01 Fuera de juego

def test_e01_comando_desconocido(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\nPase de Messi.\n{SIUUU}")
    assert errores == "CR7Script: E01 Fuera de juego (jugada 2, línea 2): no conozco la jugada «Pase de Messi»\n"


@pytest.mark.parametrize("jugada", [
    "Tiro de falta: Siempre yo",    # «:» con un prefijo que no es el Bicho
    "Agua fría",                    # palabras de más
    "Agua: algo",
    "Ay mi madre, el Bicho",        # sin «:» no es una asignación
    "Calma calma",                  # palabras de menos
])
def test_e01_variantes(tmp_path, jugada):
    errores = error_de_analisis(tmp_path, programa(jugada))
    assert errores.startswith("CR7Script: E01 Fuera de juego (jugada 2, línea 2): ")


# E02 Bicho sin balón

@pytest.mark.parametrize("oracion", ["", "   ", "autogol", "¡ 7 —", "¡Autogol!"])
def test_e02_oracion_sin_cifras(tmp_path, oracion):
    errores = error_de_analisis(tmp_path, programa(f"Ay mi madre, el Bicho:{oracion}"))
    assert errores == "CR7Script: E02 Bicho sin balón (jugada 2, línea 2): la oración no aporta ninguna cifra\n"


# E03 Sin pitido inicial

def test_e03_no_empieza_por_calma(tmp_path):
    errores = error_de_analisis(tmp_path, f"{AGUA}.\n{CALMA}.\n{SIUUU}")
    assert errores == ("CR7Script: E03 Sin pitido inicial (jugada 1, línea 1): "
                       "el partido tiene que empezar con «Calma, calma, estoy aquí»\n")


def test_e03_gana_a_e01_en_la_misma_jugada(tmp_path):
    errores = error_de_analisis(tmp_path, f"Clama, calma, estoy aquí.\n{SIUUU}")
    assert errores.startswith("CR7Script: E03 Sin pitido inicial (jugada 1, línea 1): ")


def test_e03_gana_a_e04_en_la_misma_jugada(tmp_path):
    errores = error_de_analisis(tmp_path, f"{AGUA}.")
    assert errores.startswith("CR7Script: E03 Sin pitido inicial (jugada 1, línea 1): ")


@pytest.mark.parametrize("fuente", ["", "   \n\n", "(solo un comentario)\n", "...", "﻿"])
def test_e03_archivo_sin_jugadas(tmp_path, fuente):
    errores = error_de_analisis(tmp_path, fuente)
    assert errores == "CR7Script: E03 Sin pitido inicial (línea 1): el archivo no tiene ninguna jugada\n"


def test_e03_calma_repetida(tmp_path):
    errores = error_de_analisis(tmp_path, programa(AGUA, CALMA))
    assert errores == ("CR7Script: E03 Sin pitido inicial (jugada 3, línea 3): "
                       "«Calma, calma, estoy aquí» solo puede ir al principio\n")


# E04 Sin pitido final

def test_e04_no_termina_con_siuuu(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{AGUA}.\n")
    assert errores == ("CR7Script: E04 Sin pitido final (jugada 2, línea 2): "
                       "el partido tiene que terminar con «¡Siuuu!»\n")


@pytest.mark.parametrize("fin", ["¡Siu!", "¡Siuu!", "Siuuu siuuu"])
def test_e04_gana_a_e01_en_la_ultima_jugada(tmp_path, fin):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{fin}")
    assert errores.startswith("CR7Script: E04 Sin pitido final (jugada 2, línea 2): ")


def test_e04_con_solo_el_inicio(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.")
    assert errores.startswith("CR7Script: E04 Sin pitido final (jugada 1, línea 1): ")


# E05 Partido terminado

def test_e05_jugadas_tras_siuuu(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{SIUUU}.\n{AGUA}.\n{AGUA}.")
    assert errores == ("CR7Script: E05 Partido terminado (jugada 3, línea 3): "
                       "el partido ya terminó con «¡Siuuu!»\n")


@pytest.mark.parametrize("jugada", [CALMA, "Pase de Messi", "Ay mi madre, el Bicho:", SIUUU])
def test_e05_manda_sobre_lo_que_haya_despues(tmp_path, jugada):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{SIUUU}.\n{jugada}.")
    assert errores.startswith("CR7Script: E05 Partido terminado (jugada 3, línea 3): ")


# E06 Récord sin cerrar

def test_e06_bucle_sin_cerrar(tmp_path):
    errores = error_de_analisis(tmp_path, programa(ABRIR, AGUA))
    assert errores == f"CR7Script: E06 Récord sin cerrar (jugada 2, línea 2): {TEXTO_E06}\n"


def test_e06_se_situa_en_la_apertura_exterior(tmp_path):
    errores = error_de_analisis(tmp_path, programa(AGUA, ABRIR, ABRIR, CERRAR))
    assert errores.startswith("CR7Script: E06 Récord sin cerrar (jugada 3, línea 3): ")


# E07 Récord sin perseguir

def test_e07_cierre_sin_apertura(tmp_path):
    errores = error_de_analisis(tmp_path, programa(CERRAR))
    assert errores == f"CR7Script: E07 Récord sin perseguir (jugada 2, línea 2): {TEXTO_E07}\n"


def test_e07_cierre_antes_de_su_apertura(tmp_path):
    errores = error_de_analisis(tmp_path, programa(CERRAR, ABRIR))
    assert errores.startswith("CR7Script: E07 Récord sin perseguir (jugada 2, línea 2): ")


# E08 Comentario sin cerrar

def test_e08_parentesis_sin_cerrar(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{AGUA}.\n(sin cerrar\n{SIUUU}")
    assert errores == "CR7Script: E08 Comentario sin cerrar (línea 3): falta el «)» de este comentario\n"


def test_e08_parentesis_suelto(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{AGUA}.)\n{SIUUU}")
    assert errores == "CR7Script: E08 Comentario sin cerrar (línea 2): este «)» no tiene su «(»\n"


def test_e08_sin_cerrar_no_evalua_e06(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{ABRIR}.\n({CERRAR}.\n{SIUUU}")
    assert errores.startswith("CR7Script: E08 Comentario sin cerrar (línea 3): ")


def test_e08_en_un_archivo_sin_jugadas(tmp_path):
    errores = error_de_analisis(tmp_path, "(nada")
    assert errores.startswith("CR7Script: E08 Comentario sin cerrar (línea 1): ")


@pytest.mark.parametrize("jugada, codigo", [("Pase de Messi", "E01"), (CERRAR, "E07")])
def test_e08_pierde_ante_errores_locales_anteriores(tmp_path, jugada, codigo):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{jugada}.\n(sin cerrar {SIUUU}")
    assert errores.startswith(f"CR7Script: {codigo} ")
    assert "(jugada 2, línea 2)" in errores


# Orden de los errores de análisis (§6.1)

def test_se_informa_del_primero_por_posicion(tmp_path):
    errores = error_de_analisis(tmp_path, programa("Pase de Messi", ABRIR, "Otro pase"))
    assert errores.startswith("CR7Script: E01 Fuera de juego (jugada 2, línea 2): ")


def test_e06_anterior_gana_a_e01_posterior(tmp_path):
    errores = error_de_analisis(tmp_path, programa(ABRIR, "Pase de Messi"))
    assert errores.startswith("CR7Script: E06 Récord sin cerrar (jugada 2, línea 2): ")


def test_e01_anterior_gana_a_e04(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\nPase de Messi.\n{AGUA}.")
    assert errores.startswith("CR7Script: E01 ")


def test_linea_de_una_jugada_tras_un_comentario_de_varias_lineas(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n(uno.\ndos.\ntres)\n\nPase.\n{SIUUU}")
    assert errores.startswith("CR7Script: E01 Fuera de juego (jugada 2, línea 6): ")


def test_linea_de_una_jugada_que_empieza_a_mitad_de_linea(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}. Pase.\n{SIUUU}")
    assert errores.startswith("CR7Script: E01 Fuera de juego (jugada 2, línea 1): ")


# E10 Balón fuera

def test_e10_posicion_negativa(tmp_path):
    salida, errores = error_de_ejecucion(tmp_path, programa(asignar(7), MOSTRAR_NUMERO, IZQUIERDA))
    assert salida == b"7"  # lo escrito antes del error se mantiene
    assert errores == ("CR7Script: E10 Balón fuera (jugada 4, línea 4): "
                       "no se puede volver más allá de la primera celda\n")


# E11 Revisión del VAR

@pytest.mark.parametrize("entrada, detalle", [
    (b"abc\n", "«abc» no es un número entero"),
    (b"\n", "«» no es un número entero"),
    (b"4.5\n", "«4.5» no es un número entero"),
    (b"12a", "«12a» no es un número entero"),
    (b"1 2\n", "«1 2» no es un número entero"),
    ("٣\n".encode(), "«٣» no es un número entero"),   # solo dígitos 0-9
    (b"", "la entrada ya ha terminado y faltaba un número"),
])
def test_e11_numero_no_valido(tmp_path, entrada, detalle):
    _, errores = error_de_ejecucion(tmp_path, programa(LEER_NUMERO), entrada)
    assert errores == f"CR7Script: E11 Revisión del VAR (jugada 2, línea 2): {detalle}\n"


@pytest.mark.parametrize("entrada", [b"\xff", b"\x80", b"\xc3", b"\xe2\x82", b"\xed\xa0\x80", b"\xc0\xaf"])
def test_e11_caracter_utf8_no_valido(tmp_path, entrada):
    _, errores = error_de_ejecucion(tmp_path, programa(LEER_CARACTER), entrada)
    assert errores == "CR7Script: E11 Revisión del VAR (jugada 2, línea 2): la entrada no es UTF-8 válido\n"


# E12 Grito ininteligible

@pytest.mark.parametrize("valor", [-1, 0xD800, 0xDFFF, 0x110000])
def test_e12_codigo_no_valido(tmp_path, valor):
    _, errores = error_de_ejecucion(tmp_path, programa(asignar(valor), MOSTRAR_CARACTER))
    assert errores == (f"CR7Script: E12 Grito ininteligible (jugada 3, línea 3): "
                       f"{valor} no es un código Unicode válido\n")
