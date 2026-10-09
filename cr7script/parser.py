"""Análisis sintáctico: de jugadas a instrucciones (SPEC.md §3, §4 y §6.1)."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from .errores import ErrorAnalisis
from .frases import AUTOGOL, FRASES, PREFIJO_ASIGNAR, Op, normalizar, reconocer
from .lexer import Jugada, separar


@dataclass(frozen=True)
class Instruccion:
    op: Op
    jugada: Jugada
    valor: int | None = None    # ASIGNAR: valor de la oración
    pareja: int | None = None   # bucles: índice de la instrucción emparejada


@dataclass(frozen=True)
class Programa:
    # Empieza por INICIO y termina por FIN.
    instrucciones: list[Instruccion]


def contar_letras(palabra: str) -> int:
    return sum(1 for c in unicodedata.normalize("NFC", palabra)
               if unicodedata.category(c).startswith("L"))


def valor_oracion(oracion: str) -> int | None:
    """Valor de una oración según §4.2, o None si no aporta ninguna cifra."""
    palabras = oracion.split()
    negativo = bool(palabras) and normalizar(palabras[0]) == AUTOGOL
    if negativo:
        palabras = palabras[1:]
    valor = None
    for palabra in palabras:
        letras = contar_letras(palabra)
        if letras:
            valor = (valor or 0) * 10 + letras % 10
    if valor is None:
        return None
    return -valor if negativo else valor


def _error(codigo: str, detalle: str, jugada: Jugada) -> ErrorAnalisis:
    return ErrorAnalisis(codigo, detalle, jugada.linea, jugada.numero, jugada.posicion)


def _clasificar(jugada: Jugada) -> Instruccion | ErrorAnalisis:
    """Reconoce una jugada suelta. Puede devolver E01 o E02."""
    if ":" in jugada.texto:
        prefijo, oracion = jugada.texto.split(":", 1)
        if normalizar(prefijo) != PREFIJO_ASIGNAR:
            return _error("E01", f"no conozco la jugada «{_resumen(jugada.texto)}»", jugada)
        valor = valor_oracion(oracion)
        if valor is None:
            return _error("E02", "la oración no aporta ninguna cifra", jugada)
        return Instruccion(Op.ASIGNAR, jugada, valor=valor)

    op = reconocer(normalizar(jugada.texto))
    if op is None:
        return _error("E01", f"no conozco la jugada «{_resumen(jugada.texto)}»", jugada)
    return Instruccion(op, jugada)


def _resumen(texto: str) -> str:
    return " ".join(texto.split())


def analizar(fuente: str) -> Programa:
    """Analiza un programa completo. Lanza el primer ErrorAnalisis según §6.1."""
    lexico = separar(fuente)
    errores = list(lexico.errores)
    jugadas = lexico.jugadas

    if not jugadas:
        if not errores:
            errores.append(ErrorAnalisis("E03", "el archivo no tiene ninguna jugada", 1))
        raise min(errores, key=ErrorAnalisis.clave_orden)

    instrucciones: list[Instruccion] = []
    hay_fin = False
    for jugada in jugadas:
        if hay_fin:
            # §6.1: tras el primer ¡Siuuu! toda jugada es E05.
            errores.append(_error(
                "E05", f"el partido ya terminó con «{FRASES[Op.FIN]}»", jugada))
            break
        resultado = _clasificar(jugada)
        es_inicio = isinstance(resultado, Instruccion) and resultado.op is Op.INICIO
        if jugada.numero == 1 and not es_inicio:
            errores.append(_error(
                "E03", f"el partido tiene que empezar con «{FRASES[Op.INICIO]}»", jugada))
        elif jugada.numero > 1 and es_inicio:
            errores.append(_error(
                "E03", f"«{FRASES[Op.INICIO]}» solo puede ir al principio", jugada))
        elif isinstance(resultado, ErrorAnalisis):
            errores.append(resultado)
        if isinstance(resultado, Instruccion):
            instrucciones.append(resultado)
            hay_fin = resultado.op is Op.FIN
        else:
            # Hueco para que los índices sigan alineados; nunca se ejecuta.
            instrucciones.append(Instruccion(Op.AGUA, jugada))

    # E04 y E06 dependen del resto del archivo: no se evalúan si un comentario
    # sin cerrar se lo ha tragado (§6.1).
    if not hay_fin and not lexico.comentario_abierto:
        errores.append(_error(
            "E04", f"el partido tiene que terminar con «{FRASES[Op.FIN]}»", jugadas[-1]))

    instrucciones, errores_bucles = _emparejar_bucles(instrucciones, lexico.comentario_abierto)
    errores.extend(errores_bucles)

    if errores:
        raise min(errores, key=ErrorAnalisis.clave_orden)
    return Programa(instrucciones)


def _emparejar_bucles(instrucciones: list[Instruccion], comentario_abierto: bool,
                      ) -> tuple[list[Instruccion], list[ErrorAnalisis]]:
    errores: list[ErrorAnalisis] = []
    parejas: dict[int, int] = {}
    abiertos: list[int] = []
    for i, ins in enumerate(instrucciones):
        if ins.op is Op.ABRIR_BUCLE:
            abiertos.append(i)
        elif ins.op is Op.CERRAR_BUCLE:
            if abiertos:
                apertura = abiertos.pop()
                parejas[apertura] = i
                parejas[i] = apertura
            else:
                errores.append(_error(
                    "E07", f"este «{FRASES[Op.CERRAR_BUCLE]}» no tiene ningún "
                           f"«{FRASES[Op.ABRIR_BUCLE]}» abierto", ins.jugada))
    if not comentario_abierto:
        for i in abiertos:
            errores.append(_error(
                "E06", f"este «{FRASES[Op.ABRIR_BUCLE]}» no tiene su "
                       f"«{FRASES[Op.CERRAR_BUCLE]}»", instrucciones[i].jugada))

    emparejadas = [
        Instruccion(ins.op, ins.jugada, ins.valor, parejas.get(i))
        if i in parejas else ins
        for i, ins in enumerate(instrucciones)
    ]
    return emparejadas, errores
