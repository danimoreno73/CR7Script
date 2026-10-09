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
    errores = error_de_analisis(tmp_path, f"{CALMA}.\nPase de Benzema.\n{SIUUU}")
    assert errores == "CR7Script: E01 Fuera de juego (jugada 2, línea 2): no conozco la jugada «Pase de Benzema»\n"


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

@pytest.mark.parametrize("oracion", ["", "   ", "autogol", "¡ , !", "¡Autogol!", "autogol ¡"])
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


@pytest.mark.parametrize("jugada", [CALMA, "Pase de Benzema", "Ay mi madre, el Bicho:", SIUUU])
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


@pytest.mark.parametrize("jugada, codigo", [("Pase de Benzema", "E01"), (CERRAR, "E07")])
def test_e08_pierde_ante_errores_locales_anteriores(tmp_path, jugada, codigo):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{jugada}.\n(sin cerrar {SIUUU}")
    assert errores.startswith(f"CR7Script: {codigo} ")
    assert "(jugada 2, línea 2)" in errores


# E09 No convocado

def test_e09_palabra_no_convocada(tmp_path):
    errores = error_de_analisis(tmp_path, programa("Ay mi madre, el Bicho: Ronaldo Siempre yo"))
    assert errores == ("CR7Script: E09 No convocado (jugada 2, línea 2): "
                       "«Siempre» no está en la lista de convocados\n")


def test_e09_se_situa_en_la_jugada_donde_aparece(tmp_path):
    fuente = programa(AGUA, "Ay mi madre, el Bicho:\n  Ronaldo\n  CR9", "Pase de Benzema")
    errores = error_de_analisis(tmp_path, fuente)
    assert errores.startswith("CR7Script: E09 No convocado (jugada 3, línea 3): ")


def test_e09_pierde_ante_e03_en_la_misma_jugada(tmp_path):
    errores = error_de_analisis(tmp_path, f"Ay mi madre, el Bicho: Siempre.\n{SIUUU}")
    assert errores.startswith("CR7Script: E03 ")


def test_e09_pierde_ante_e04_en_la_misma_jugada(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\nAy mi madre, el Bicho: Siempre.")
    assert errores.startswith("CR7Script: E04 ")


def test_e09_anterior_gana_a_un_e06_posterior(tmp_path):
    errores = error_de_analisis(tmp_path, programa("Ay mi madre, el Bicho: —", ABRIR))
    assert errores.startswith("CR7Script: E09 No convocado (jugada 2, línea 2): ")


# E13 Roja directa

PROHIBIDAS = ["Messi", "Leo", "Lionel", "Pulga", "Lamine", "Yamal", "Mundial", "Qatar", "Penaldo"]


def mensaje_e13(palabra, jugada=2, linea=2):
    return (f"CR7Script: E13 Roja directa (jugada {jugada}, línea {linea}): "
            f"«{palabra}» es una palabra prohibida\n")


@pytest.mark.parametrize("palabra", PROHIBIDAS)
def test_e13_dentro_de_una_oracion(tmp_path, palabra):
    # Gana a E09, que también se daría porque la palabra no está convocada.
    errores = error_de_analisis(tmp_path, programa(f"Ay mi madre, el Bicho: Ronaldo {palabra} yo"))
    assert errores == mensaje_e13(palabra)


@pytest.mark.parametrize("palabra", PROHIBIDAS)
def test_e13_fuera_de_una_oracion(tmp_path, palabra):
    # Gana a E01, que también se daría porque la jugada no es ninguna frase.
    errores = error_de_analisis(tmp_path, programa(f"Pase de {palabra}"))
    assert errores == mensaje_e13(palabra)


@pytest.mark.parametrize("palabra", PROHIBIDAS)
def test_e13_pegada_a_una_frase_valida(tmp_path, palabra):
    errores = error_de_analisis(tmp_path, programa(f"{AGUA} {palabra}"))
    assert errores == mensaje_e13(palabra)


@pytest.mark.parametrize("palabra", [
    "MESSI", "messi", "Messí", "MÉSSI", "léo", "LIONEL", "Pülga", "lamíne", "YAMAL",
    "mundïal", "QATAR", "Qátar", "PENALDO", "Penáldo",
])
def test_e13_con_mayusculas_y_tildes_distintas(tmp_path, palabra):
    errores = error_de_analisis(tmp_path, programa(f"Ay mi madre, el Bicho: {palabra}"))
    assert errores == mensaje_e13(palabra)


@pytest.mark.parametrize("texto, palabra", [
    ("¡Messi!", "Messi"),
    ("¿Leo?", "Leo"),
    ("Messi:", "Messi"),
    ("Qatar-2022", "Qatar"),
    ("Messi10", "Messi"),
    ("Lamine Yamal", "Lamine"),       # se informa de la primera
    ("Yamal y Lamine", "Yamal"),
])
def test_e13_palabra_a_palabra(tmp_path, texto, palabra):
    errores = error_de_analisis(tmp_path, programa(f"Pase de {texto}"))
    assert errores == mensaje_e13(palabra)


def test_e13_con_las_palabras_descompuestas_en_nfd(tmp_path):
    errores = error_de_analisis(tmp_path, programa("Pase de Méssi"))
    assert errores == mensaje_e13("Méssi")


@pytest.mark.parametrize("texto", ["Leopoldo", "MessiScript", "Pulgas", "Qatari"])
def test_no_es_e13_si_la_palabra_es_otra(tmp_path, texto):
    errores = error_de_analisis(tmp_path, programa(f"Pase de {texto}"))
    assert errores.startswith("CR7Script: E01 ")


def test_dentro_de_un_comentario_se_permite(tmp_path):
    fuente = f"{CALMA}. (Messi, Leo, Lionel, Pulga, Lamine Yamal, Mundial, Qatar, Penaldo)\n{SIUUU}"
    assert lanzar(tmp_path, fuente) == (0, b"", "")


def test_e13_en_una_jugada_que_ocupa_varias_lineas(tmp_path):
    errores = error_de_analisis(tmp_path, programa(f"{MOSTRAR_NUMERO}\n  y Messi"))
    assert errores == mensaje_e13("Messi")


def test_e13_gana_a_e09_aunque_la_no_convocada_vaya_antes(tmp_path):
    errores = error_de_analisis(tmp_path, programa("Ay mi madre, el Bicho: Siempre Messi"))
    assert errores == mensaje_e13("Messi")


def test_e13_pierde_ante_e03_en_la_primera_jugada(tmp_path):
    errores = error_de_analisis(tmp_path, f"Messi.\n{SIUUU}")
    assert errores.startswith("CR7Script: E03 Sin pitido inicial (jugada 1, línea 1): ")


def test_e13_pierde_ante_e03_con_la_frase_de_inicio_alterada(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}, Messi.\n{SIUUU}")
    assert errores.startswith("CR7Script: E03 Sin pitido inicial (jugada 1, línea 1): ")


@pytest.mark.parametrize("ultima", ["Messi", "¡Siuuu! Messi"])
def test_e13_pierde_ante_e04_en_la_ultima_jugada(tmp_path, ultima):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{AGUA}.\n{ultima}")
    assert errores.startswith("CR7Script: E04 Sin pitido final (jugada 3, línea 3): ")


def test_e13_pierde_ante_e05_tras_el_pitido_final(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\n{SIUUU}.\nMessi.")
    assert errores.startswith("CR7Script: E05 Partido terminado (jugada 3, línea 3): ")


def test_e13_anterior_gana_a_errores_posteriores(tmp_path):
    errores = error_de_analisis(tmp_path, programa("Pase de Leo", "Pase de Benzema", ABRIR))
    assert errores == mensaje_e13("Leo")


def test_errores_anteriores_ganan_a_e13_posterior(tmp_path):
    errores = error_de_analisis(tmp_path, programa("Pase de Benzema", "Pase de Leo"))
    assert errores.startswith("CR7Script: E01 Fuera de juego (jugada 2, línea 2): ")


def test_e13_anterior_a_un_comentario_sin_cerrar(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\nPase de Leo.\n(sin cerrar {SIUUU}")
    assert errores == mensaje_e13("Leo")


# Orden de los errores de análisis (§6.1)

def test_se_informa_del_primero_por_posicion(tmp_path):
    errores = error_de_analisis(tmp_path, programa("Pase de Benzema", ABRIR, "Otro pase"))
    assert errores.startswith("CR7Script: E01 Fuera de juego (jugada 2, línea 2): ")


def test_e06_anterior_gana_a_e01_posterior(tmp_path):
    errores = error_de_analisis(tmp_path, programa(ABRIR, "Pase de Benzema"))
    assert errores.startswith("CR7Script: E06 Récord sin cerrar (jugada 2, línea 2): ")


def test_e01_anterior_gana_a_e04(tmp_path):
    errores = error_de_analisis(tmp_path, f"{CALMA}.\nPase de Benzema.\n{AGUA}.")
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
