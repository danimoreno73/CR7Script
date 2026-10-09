"""Intérprete de CR7Script. La definición del lenguaje está en SPEC.md."""

import sys

from .errores import ErrorAnalisis, ErrorCR7, ErrorEjecucion
from .interprete import Estado, ejecutar
from .parser import Programa, analizar

# §1: los enteros son de precisión arbitraria, también al leerlos y escribirlos
# en decimal (Python limita por defecto la conversión a 4300 cifras).
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

__all__ = [
    "ErrorAnalisis", "ErrorCR7", "ErrorEjecucion",
    "Estado", "Programa", "analizar", "ejecutar",
]
