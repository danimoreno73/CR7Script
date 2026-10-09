"""Utilidades para los tests.

Las frases se escriben aquí a mano, sin importarlas de cr7script.frases, para
que los tests comprueben de verdad el lenguaje de SPEC.md.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

from cr7script import analizar, ejecutar
from cr7script.__main__ import main

RAIZ = Path(__file__).resolve().parent.parent
SPEC = (RAIZ / "SPEC.md").read_text(encoding="utf-8")

INICIO = "Calma, calma, estoy aquí"
FIN = "¡Siuuu!"
DERECHA = "Fue muy bonito estar en el Madrid"
IZQUIERDA = "He vuelto a casa"
BICHO = "Ay mi madre, el Bicho:"
AGUA = "Agua"
MOSTRAR_NUMERO = "Soy el primero, el segundo y el tercero"
MOSTRAR_CARACTER = "¿Eres de Málaga? Quichiano, quichiano"
LEER_NUMERO = "Más un poco y estás aquí, madre mía hijo mío"
LEER_CARACTER = "Anda a patear, muestra personalidad"
ABRIR = "Yo no persigo los récords"
CERRAR = "Los récords me persiguen a mí"
COPIAR = "Me tienen envidia"
PEGAR = "Rico, guapo y gran jugador"
CHILENA = "Chilena en Turín"
SUMAR = "Losh dosh"
PENALTI = "El penalti lo tiro yo"


# Una palabra convocada para cada cifra (Anexo A).
PALABRA_DE_CIFRA = {
    "0": "Portuguesa", "1": "y", "2": "de", "3": "gol", "4": "Liga",
    "5": "Bicho", "6": "Madrid", "7": "Ronaldo", "8": "Portugal", "9": "Cristiano",
}


def asignar(valor: int) -> str:
    """Jugada de asignación con una oración que vale exactamente `valor`."""
    palabras = [PALABRA_DE_CIFRA[c] for c in str(abs(valor))]
    if valor < 0:
        palabras.insert(0, "autogol")
    return f"{BICHO} {' '.join(palabras)}"


def programa(*jugadas: str) -> str:
    """Programa completo: inicio, las jugadas dadas y fin."""
    return ".\n".join([INICIO, *jugadas, FIN])


def correr(*jugadas: str, entrada: bytes = b""):
    """Analiza y ejecuta un programa. Devuelve (estado final, bytes escritos)."""
    salida = io.BytesIO()
    estado = ejecutar(analizar(programa(*jugadas)), io.BytesIO(entrada), salida)
    return estado, salida.getvalue()


def lanzar(tmp_path: Path, fuente: str | bytes, entrada: bytes = b""):
    """Ejecuta la CLI sobre un archivo. Devuelve (código, salida, errores)."""
    archivo = tmp_path / "programa.siu"
    if isinstance(fuente, str):
        fuente = fuente.encode("utf-8")
    archivo.write_bytes(fuente)
    salida, errores = io.BytesIO(), io.BytesIO()
    codigo = main([str(archivo)], io.BytesIO(entrada), salida, errores)
    return codigo, salida.getvalue(), errores.getvalue().decode("utf-8")


def seccion(titulo: str) -> str:
    """Texto de una sección de SPEC.md, desde su título hasta el siguiente."""
    inicio = SPEC.index(titulo)
    siguiente = re.search(r"^##+ ", SPEC[inicio + len(titulo):], re.M)
    fin = inicio + len(titulo) + (siguiente.start() if siguiente else len(SPEC))
    return SPEC[inicio:fin]
