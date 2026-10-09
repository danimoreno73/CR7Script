"""Tabla única de frases de CR7Script (SPEC.md §3) y su normalización (§2.2).

Todo el intérprete reconoce las jugadas a partir de esta tabla. Si cambia una
frase, se cambia aquí y en SPEC.md; tests/test_frases.py comprueba que las dos
coinciden.
"""

from __future__ import annotations

import enum
import re
import unicodedata


class Op(enum.Enum):
    """Comandos del lenguaje. El valor es el número de la tabla de §3."""

    INICIO = 1
    FIN = 2
    DERECHA = 3
    IZQUIERDA = 4
    ASIGNAR = 5
    AGUA = 6
    MOSTRAR_NUMERO = 7
    MOSTRAR_CARACTER = 8
    LEER_NUMERO = 9
    LEER_CARACTER = 10
    ABRIR_BUCLE = 11
    CERRAR_BUCLE = 12
    COPIAR = 13
    PEGAR = 14
    CHILENA = 15
    SUMAR = 16
    PENALTI = 17


# Frase canónica de cada comando, escrita como en SPEC.md §3.
# ASIGNAR es solo la parte anterior a los dos puntos; FIN es la forma mínima.
FRASES: dict[Op, str] = {
    Op.INICIO: "Calma, calma, estoy aquí",
    Op.FIN: "¡Siuuu!",
    Op.DERECHA: "Fue muy bonito estar en el Madrid",
    Op.IZQUIERDA: "He vuelto a casa",
    Op.ASIGNAR: "Ay mi madre, el Bicho",
    Op.AGUA: "Agua",
    Op.MOSTRAR_NUMERO: "Soy el primero, el segundo y el tercero",
    Op.MOSTRAR_CARACTER: "¿Eres de Málaga? Quichiano, quichiano",
    Op.LEER_NUMERO: "Más un poco y estás aquí, madre mía hijo mío",
    Op.LEER_CARACTER: "Anda a patear, muestra personalidad",
    Op.ABRIR_BUCLE: "Yo no persigo los récords",
    Op.CERRAR_BUCLE: "Los récords me persiguen a mí",
    Op.COPIAR: "Me tienen envidia",
    Op.PEGAR: "Rico, guapo y gran jugador",
    Op.CHILENA: "Chilena en Turín",
    Op.SUMAR: "Losh dosh",
    Op.PENALTI: "El penalti lo tiro yo",
}

_SIGNOS_IGNORADOS = str.maketrans("", "", "¡!¿?,;")

# §4.1: el fin admite tres «u» o más.
PATRON_FIN = re.compile(r"siu{3,}")


def normalizar(texto: str) -> str:
    """Normaliza un texto según §2.2."""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.translate(_SIGNOS_IGNORADOS)
    return " ".join(texto.split())


PREFIJO_ASIGNAR = normalizar(FRASES[Op.ASIGNAR])

# Comandos que se reconocen comparando la jugada entera con su forma normalizada.
POR_FORMA: dict[str, Op] = {
    normalizar(frase): op
    for op, frase in FRASES.items()
    if op not in (Op.FIN, Op.ASIGNAR)
}


def reconocer(jugada_normalizada: str) -> Op | None:
    """Devuelve el comando de una jugada sin dos puntos, o None si no existe."""
    if PATRON_FIN.fullmatch(jugada_normalizada):
        return Op.FIN
    return POR_FORMA.get(jugada_normalizada)
