"""Ejecución de un programa ya analizado (SPEC.md §1, §4 y §5)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import BinaryIO

from .errores import ErrorEjecucion
from .frases import Op
from .parser import Instruccion, Programa

_ENTERO = re.compile(r"[+-]?[0-9]+")


@dataclass
class Estado:
    campo: list[int] = field(default_factory=lambda: [0])
    posicion: int = 0
    portapapeles: int = 0

    @property
    def celda(self) -> int:
        return self.campo[self.posicion]

    @celda.setter
    def celda(self, valor: int) -> None:
        self.campo[self.posicion] = valor


class Entrada:
    """Lee de un flujo binario línea a línea o carácter a carácter (§4.3)."""

    def __init__(self, flujo: BinaryIO):
        self._flujo = flujo

    def leer_linea(self) -> bytes | None:
        """Devuelve la línea sin el salto final, o None si ya no hay entrada."""
        datos = bytearray()
        while True:
            byte = self._flujo.read(1)
            if not byte:
                return bytes(datos) if datos else None
            if byte == b"\n":
                return bytes(datos)
            datos += byte

    def leer_caracter(self) -> str | None:
        """Devuelve un carácter, o None si ya no hay entrada.

        Lanza UnicodeDecodeError si los bytes no forman UTF-8 válido.
        """
        primero = self._flujo.read(1)
        if not primero:
            return None
        inicial = primero[0]
        if inicial < 0x80:
            longitud = 1
        elif 0xC2 <= inicial <= 0xDF:
            longitud = 2
        elif 0xE0 <= inicial <= 0xEF:
            longitud = 3
        elif 0xF0 <= inicial <= 0xF4:
            longitud = 4
        else:
            longitud = 1  # byte que no puede empezar un carácter
        datos = primero + self._flujo.read(longitud - 1)
        return datos.decode("utf-8")


def ejecutar(programa: Programa, entrada: BinaryIO, salida: BinaryIO) -> Estado:
    """Ejecuta el programa. Lanza ErrorEjecucion (E10–E12) si algo falla."""
    estado = Estado()
    lector = Entrada(entrada)
    instrucciones = programa.instrucciones
    fin = len(instrucciones) - 1
    pc = 1  # la instrucción 0 es el inicio
    while pc < fin:
        ins = instrucciones[pc]
        op = ins.op
        if op is Op.DERECHA:
            estado.posicion += 1
            if estado.posicion == len(estado.campo):
                estado.campo.append(0)
        elif op is Op.IZQUIERDA:
            if estado.posicion == 0:
                raise _error("E10", "no se puede volver más allá de la primera celda", ins)
            estado.posicion -= 1
        elif op is Op.ASIGNAR:
            estado.celda = ins.valor
        elif op is Op.AGUA:
            estado.celda = 0
        elif op is Op.MOSTRAR_NUMERO:
            salida.write(str(estado.celda).encode("ascii"))
        elif op is Op.MOSTRAR_CARACTER:
            salida.write(_caracter(estado.celda, ins).encode("utf-8"))
        elif op is Op.LEER_NUMERO:
            estado.celda = _leer_numero(lector, ins)
        elif op is Op.LEER_CARACTER:
            estado.celda = _leer_caracter(lector, ins)
        elif op is Op.ABRIR_BUCLE:
            if estado.celda <= 0:
                pc = ins.pareja
        elif op is Op.CERRAR_BUCLE:
            if estado.celda > 0:
                pc = ins.pareja
        elif op is Op.COPIAR:
            estado.portapapeles = estado.celda
        elif op is Op.PEGAR:
            estado.celda = estado.portapapeles
        elif op is Op.CHILENA:
            estado.celda, estado.portapapeles = estado.portapapeles, estado.celda
        elif op is Op.SUMAR:
            estado.celda += estado.portapapeles
        elif op is Op.PENALTI:
            if estado.celda == 0:
                pc += 1
        pc += 1
    return estado


def _error(codigo: str, detalle: str, ins: Instruccion) -> ErrorEjecucion:
    return ErrorEjecucion(codigo, detalle, ins.jugada.linea, ins.jugada.numero)


def _caracter(valor: int, ins: Instruccion) -> str:
    if 0 <= valor <= 0x10FFFF and not 0xD800 <= valor <= 0xDFFF:
        return chr(valor)
    raise _error("E12", f"{valor} no es un código Unicode válido", ins)


def _leer_numero(lector: Entrada, ins: Instruccion) -> int:
    linea = lector.leer_linea()
    if linea is None:
        raise _error("E11", "la entrada ya ha terminado y faltaba un número", ins)
    texto = linea.decode("utf-8", errors="replace").strip()
    if not _ENTERO.fullmatch(texto):
        raise _error("E11", f"«{texto}» no es un número entero", ins)
    return int(texto)


def _leer_caracter(lector: Entrada, ins: Instruccion) -> int:
    try:
        caracter = lector.leer_caracter()
    except UnicodeDecodeError:
        raise _error("E11", "la entrada no es UTF-8 válido", ins) from None
    return 0 if caracter is None else ord(caracter)
