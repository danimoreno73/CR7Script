"""Bucles (SPEC.md §4.4) y su relación con el penalti (§5.3)."""

from tests.ayuda import (
    ABRIR, BICHO, CERRAR, COPIAR, DERECHA, IZQUIERDA, MOSTRAR_CARACTER,
    MOSTRAR_NUMERO, PEGAR, PENALTI, SUMAR, asignar, correr,
)


def decrementar():
    """Jugadas que dejan -1 en el portapapeles."""
    return [asignar(-1), COPIAR]


def test_bucle_con_celda_a_cero_no_entra():
    _, salida = correr(ABRIR, asignar(7), MOSTRAR_NUMERO, CERRAR)
    assert salida == b""


def test_bucle_se_repite_hasta_que_la_celda_vale_cero():
    _, salida = correr(*decrementar(), asignar(3),
                       ABRIR, MOSTRAR_NUMERO, SUMAR, CERRAR)
    assert salida == b"321"


def test_bucles_anidados_dibujan_un_triangulo():
    # c0: filas pendientes; c1: asteriscos pendientes; c2: auxiliar.
    estado, salida = correr(
        asignar(3),
        ABRIR,
            COPIAR, DERECHA, PEGAR,                 # c1 = c0
            DERECHA, *decrementar(), IZQUIERDA,     # portapapeles = -1
            ABRIR,
                DERECHA, asignar(42), MOSTRAR_CARACTER, IZQUIERDA,
                SUMAR,
            CERRAR,
            DERECHA, asignar(10), MOSTRAR_CARACTER, IZQUIERDA, IZQUIERDA,
            SUMAR,
        CERRAR,
    )
    assert salida == b"***\n**\n*\n"
    assert estado.campo[:2] == [0, 0]


def test_bucle_interior_que_no_se_ejecuta():
    _, salida = correr(
        *decrementar(), asignar(2),
        ABRIR,
            DERECHA, ABRIR, asignar(9), MOSTRAR_NUMERO, CERRAR, IZQUIERDA,
            MOSTRAR_NUMERO, SUMAR,
        CERRAR,
    )
    assert salida == b"21"


def test_tres_niveles_de_anidamiento():
    # Cuenta 2 * 2 * 2 vueltas del cuerpo más interno.
    estado, _ = correr(
        asignar(2), DERECHA, *decrementar(), IZQUIERDA,
        ABRIR,
            DERECHA, asignar(2),
            ABRIR,
                DERECHA, asignar(2),
                ABRIR,
                    DERECHA, DERECHA, asignar(1), COPIAR, DERECHA, SUMAR,
                    IZQUIERDA, asignar(-1), COPIAR, IZQUIERDA, IZQUIERDA, SUMAR,
                CERRAR,
                IZQUIERDA, SUMAR,
            CERRAR,
            IZQUIERDA, SUMAR,
        CERRAR,
    )
    assert estado.campo[5] == 8


def test_penalti_que_salta_la_apertura_entra_sin_comprobar():
    _, salida = correr(PENALTI, ABRIR, MOSTRAR_NUMERO, CERRAR)
    assert salida == b"0"


def test_penalti_que_salta_el_cierre_sale_sin_volver():
    _, salida = correr(
        *decrementar(), asignar(3),
        ABRIR,
            MOSTRAR_NUMERO, SUMAR, SUMAR, SUMAR,   # 3 -> 0
            PENALTI,
        CERRAR,
        f"{BICHO} Siempre yo", MOSTRAR_NUMERO,
    )
    assert salida == b"372"
