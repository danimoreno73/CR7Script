"""Errores de CR7Script (SPEC.md §6)."""

from __future__ import annotations

NOMBRES: dict[str, str] = {
    "E01": "Fuera de juego",
    "E02": "Bicho sin balón",
    "E03": "Sin pitido inicial",
    "E04": "Sin pitido final",
    "E05": "Partido terminado",
    "E06": "Récord sin cerrar",
    "E07": "Récord sin perseguir",
    "E08": "Comentario sin cerrar",
    "E10": "Balón fuera",
    "E11": "Revisión del VAR",
    "E12": "Grito ininteligible",
}

# §6.1: si dos errores de análisis caen en la misma posición, ganan los
# estructurales (E03, E04, E05) y, entre ellos, E03 antes que E04.
_PRIORIDAD = {"E03": 0, "E04": 1, "E05": 2}
_PRIORIDAD_RESTO = 3


class ErrorCR7(Exception):
    """Error con código y nombre de la spec, listo para mostrarse."""

    def __init__(self, codigo: str, detalle: str, linea: int, jugada: int | None = None):
        self.codigo = codigo
        self.nombre = NOMBRES[codigo]
        self.detalle = detalle
        self.linea = linea
        self.jugada = jugada
        super().__init__(self.mensaje())

    def mensaje(self) -> str:
        if self.jugada is None:
            lugar = f"línea {self.linea}"
        else:
            lugar = f"jugada {self.jugada}, línea {self.linea}"
        return f"CR7Script: {self.codigo} {self.nombre} ({lugar}): {self.detalle}"


class ErrorAnalisis(ErrorCR7):
    """Error detectado antes de ejecutar (E01–E08). Código de salida 1."""

    def __init__(self, codigo: str, detalle: str, linea: int,
                 jugada: int | None = None, posicion: int = 0):
        # posicion: índice del carácter del fuente donde se sitúa el error.
        self.posicion = posicion
        super().__init__(codigo, detalle, linea, jugada)

    def clave_orden(self) -> tuple[int, int]:
        return self.posicion, _PRIORIDAD.get(self.codigo, _PRIORIDAD_RESTO)


class ErrorEjecucion(ErrorCR7):
    """Error durante la ejecución (E10–E12). Código de salida 2."""
