"""Vocabulario de CR7Script (SPEC.md Anexo A).

Contiene la única lista de palabras que el intérprete admite en la oración de
«Ay mi madre, el Bicho:» y la lista de palabras prohibidas en cualquier
jugada. Si cambian, se cambian aquí y en el Anexo A de SPEC.md;
tests/test_vocabulario.py comprueba que coinciden.
"""

from __future__ import annotations

import re
import unicodedata

from .frases import normalizar

# §4.2: como primera palabra, vuelve negativa la oración y no aporta cifra.
AUTOGOL = "autogol"

# Cifra -> palabras. La cifra es el número de letras módulo 10.
CONECTORES: dict[int, tuple[str, ...]] = {
    1: ("y", "a", "o", "e"),
    2: ("de", "el", "la", "en", "al", "lo", "yo", "mi"),
    3: ("con", "del", "los", "las", "por", "que", "más"),
}

TEMATICAS: dict[int, tuple[str, ...]] = {
    0: ("Manchester", "Portuguesa", "Campeonato", "Tricampeón", "Goleadores",
        "Futbolista", "Madridista", "Asistencia", "Entrenador", "Delanteros"),
    1: ("Madridistas", "Portugueses", "Futbolistas", "Campeonatos", "Asistencias",
        "Celebración", "Abdominales"),
    2: ("Pentacampeón", "Tetracampeón", "Entrenadores", "Futbolístico"),
    3: ("gol", "oro", "VAR", "Old", "Nou", "Luz", "Metropolitano", "Entrenamiento",
        "Internacional", "Decimotercera", "Celebraciones"),
    4: ("Real", "Liga", "Copa", "Bota", "Juve", "Pepe", "Nani", "Bale", "Kaká", "Isco",
        "Xavi", "Kiev", "Riad", "Roma", "Camp", "City", "pase", "tiro", "giro"),
    5: ("Bicho", "Calma", "Siuuu", "Turín", "Milán", "Moscú", "París", "Nassr",
        "Kroos", "Ramos", "Bruno", "Barça", "Piqué", "Puyol", "Tevez", "Giggs", "balón",
        "falta", "goles", "final", "póker", "siete", "salto", "grito"),
    6: ("Madrid", "United", "Lisboa", "Oporto", "Zagreb", "España", "Aveiro", "Modric",
        "Rooney", "Dybala", "Buffon", "Alonso", "Varane", "Zidane", "Bayern", "Neymar",
        "Mbappé", "Valdés", "récord", "golazo", "remate", "regate", "dorsal", "Décima"),
    7: ("Ronaldo", "Funchal", "Madeira", "Cardiff", "Hungría", "Polonia", "Francia",
        "Benzema", "Marcelo", "Scholes", "Bonucci", "Higuaín", "Iniesta", "Simeone",
        "Chelsea", "Allianz", "Premier", "Orejona", "penalti", "chilena",
        "trivela", "doblete", "capitán", "extremo", "campeón", "récords"),
    8: ("Portugal", "Sporting", "Juventus", "Nacional", "Bernabéu", "Alvalade",
        "Trafford", "Marsella", "Budapest", "Casillas", "Moutinho", "Quaresma",
        "Carvajal", "Ferguson", "Mourinho", "Atlético", "Eurocopa", "Pichichi",
        "Scudetto", "Undécima", "Triplete", "Cabezazo", "Goleador", "penaltis"),
    9: ("Cristiano", "Champions", "Andorinha", "Selección", "Barcelona", "Liverpool",
        "Argentina", "Ferdinand", "Chiellini", "Ancelotti", "Fernandes", "Guardiola",
        "Supercopa", "Duodécima", "Bicicleta", "Delantero", "Remontada", "Campeones"),
}

# Únicos tokens con dígitos admitidos: «7», por su dorsal, y «CR7», por sus
# tres caracteres.
ESPECIALES: dict[str, int] = {"7": 7, "CR7": 3}


def contar_letras(palabra: str) -> int:
    """Número de letras (categoría Unicode L, tras normalizar a NFC)."""
    return sum(1 for c in unicodedata.normalize("NFC", palabra)
               if unicodedata.category(c).startswith("L"))


_CIFRAS: dict[str, int] = {
    normalizar(palabra): cifra
    for grupo in (CONECTORES, TEMATICAS)
    for cifra, palabras in grupo.items()
    for palabra in palabras
}
_CIFRAS.update({normalizar(token): cifra for token, cifra in ESPECIALES.items()})


def cifra(palabra_normalizada: str) -> int | None:
    """Cifra que aporta una palabra ya normalizada, o None si no está convocada."""
    return _CIFRAS.get(palabra_normalizada)


# §2.6: prohibidas en cualquier jugada, dentro o fuera de una oración.
PROHIBIDAS: tuple[str, ...] = (
    "Messi", "Leo", "Lionel", "Pulga", "Lamine", "Yamal", "Mundial", "Qatar", "Penaldo",
)

_PROHIBIDAS = frozenset(normalizar(p) for p in PROHIBIDAS)

# Una palabra, a efectos de §2.6, es cada secuencia seguida de letras.
_PALABRA = re.compile(r"[^\W\d_]+")


def buscar_prohibida(texto: str) -> str | None:
    """Primera palabra prohibida del texto, tal como está escrita, o None."""
    for palabra in _PALABRA.findall(unicodedata.normalize("NFC", texto)):
        if normalizar(palabra) in _PROHIBIDAS:
            return palabra
    return None
