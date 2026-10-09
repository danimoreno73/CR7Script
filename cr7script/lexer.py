"""Análisis léxico: comentarios y separación en jugadas (SPEC.md §2.1 y §2.3)."""

from __future__ import annotations

from dataclasses import dataclass, field

from .errores import ErrorAnalisis

BOM = "﻿"


@dataclass(frozen=True)
class Jugada:
    numero: int     # desde 1, sin contar fragmentos vacíos
    texto: str      # sin comentarios y sin espacios en los extremos
    posicion: int   # índice en el fuente de su primer carácter
    linea: int


@dataclass
class Lexico:
    jugadas: list[Jugada] = field(default_factory=list)
    errores: list[ErrorAnalisis] = field(default_factory=list)
    # True si queda un «(» sin cerrar: el resto del archivo no se puede analizar.
    comentario_abierto: bool = False


def numero_de_linea(fuente: str, posicion: int) -> int:
    return fuente.count("\n", 0, posicion) + 1


def separar(fuente: str) -> Lexico:
    """Quita los comentarios y divide el fuente en jugadas."""
    if fuente.startswith(BOM):
        # Se sustituye por un espacio para no mover las posiciones.
        fuente = " " + fuente[1:]

    lexico = Lexico()
    limpio: list[str] = []
    origen: list[int] = []  # origen[i]: posición en el fuente de limpio[i]
    inicio_comentario: int | None = None

    for i, c in enumerate(fuente):
        if inicio_comentario is not None:
            if c == ")":
                inicio_comentario = None
            continue
        if c == "(":
            inicio_comentario = i
        elif c == ")":
            lexico.errores.append(ErrorAnalisis(
                "E08", "este «)» no tiene su «(»",
                numero_de_linea(fuente, i), posicion=i))
        else:
            limpio.append(c)
            origen.append(i)

    if inicio_comentario is not None:
        lexico.comentario_abierto = True
        lexico.errores.append(ErrorAnalisis(
            "E08", "falta el «)» de este comentario",
            numero_de_linea(fuente, inicio_comentario), posicion=inicio_comentario))

    texto = "".join(limpio)
    inicio = 0
    for fin in [*(i for i, c in enumerate(texto) if c == "."), len(texto)]:
        fragmento = texto[inicio:fin]
        recortado = fragmento.strip()
        if recortado:
            primer = inicio + (len(fragmento) - len(fragmento.lstrip()))
            posicion = origen[primer]
            lexico.jugadas.append(Jugada(
                numero=len(lexico.jugadas) + 1,
                texto=recortado,
                posicion=posicion,
                linea=numero_de_linea(fuente, posicion),
            ))
        inicio = fin + 1

    return lexico
