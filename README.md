# CR7Script

CR7Script es un lenguaje de programación esotérico en el que cada programa es
una jugada de Cristiano Ronaldo. Los comandos son frases suyas en español,
separadas por puntos; los valores se dan con oraciones de vocabulario
futbolero, y todo programa termina con un `¡Siuuu!`.

La definición completa del lenguaje está en [SPEC.md](SPEC.md). Este README es
un resumen.

## Hola mundo

[`ejemplos/hola_mundo.siu`](ejemplos/hola_mundo.siu) escribe `Hola, mundo!` y
un salto de línea:

```
Calma, calma, estoy aquí.

Ay mi madre, el Bicho: Ronaldo yo.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: Madridistas y portugueses.
¿Eres de Málaga? Quichiano, quichiano.
Me tienen envidia.

Ay mi madre, el Bicho: Y Manchester, Juventus.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: Cristiano 7.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: Liga, Copa.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: CR7 yo.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: Y Manchester, Champions.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: Madridistas y Ronaldo.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: Portugueses y goleadores.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: Futbolistas, goleadores, tricampeón.
¿Eres de Málaga? Quichiano, quichiano.

Rico, guapo y gran jugador.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: ¡Gol, gol!.
¿Eres de Málaga? Quichiano, quichiano.

Ay mi madre, el Bicho: A Portuguesa.
¿Eres de Málaga? Quichiano, quichiano.

¡Siuuu!
```

Cada `Ay mi madre, el Bicho:` pone en la celda el código de un carácter
(`Ronaldo yo` vale 72, la `H`) y `¿Eres de Málaga? Quichiano, quichiano` lo
escribe. La `o` se guarda con `Me tienen envidia` y se recupera con
`Rico, guapo y gran jugador`.

## Modelo de ejecución

Un programa trabaja sobre tres cosas
([SPEC.md §1](SPEC.md#1-modelo-de-ejecución)):

- **Campo:** una lista de enteros de precisión arbitraria. Empieza con una
  celda a `0` y crece por la derecha cuando hace falta.
- **Posición:** la celda actual. Empieza en `0` y nunca puede ser negativa.
- **Portapapeles:** un entero aparte, que empieza en `0`.

Las jugadas se separan con puntos y se reconocen sin distinguir mayúsculas,
tildes ni los signos `¡ ! ¿ ? , ;`. Lo que va entre paréntesis es un
comentario.

## Comandos

| # | Frase | Efecto |
|---|---|---|
| 1 | `Calma, calma, estoy aquí` | Inicio del programa (siempre la primera jugada). |
| 2 | `¡Siuuu!` | Fin del programa (siempre la última; tres `u` o más). |
| 3 | `Fue muy bonito estar en el Madrid` | Mueve la posición a la derecha. |
| 4 | `He vuelto a casa` | Mueve la posición a la izquierda. |
| 5 | `Ay mi madre, el Bicho: <oración>` | Asigna a la celda el valor de la oración. |
| 6 | `Agua` | Pone la celda a `0`. |
| 7 | `Soy el primero, el segundo y el tercero` | Escribe la celda como número. |
| 8 | `¿Eres de Málaga? Quichiano, quichiano` | Escribe la celda como carácter Unicode. |
| 9 | `Más un poco y estás aquí, madre mía hijo mío` | Lee un número entero (una línea). |
| 10 | `Anda a patear, muestra personalidad` | Lee un carácter (0 al final de la entrada). |
| 11 | `Yo no persigo los récords` | Abre un bucle: si la celda no es mayor que `0`, salta tras su cierre. |
| 12 | `Los récords me persiguen a mí` | Cierra el bucle: si la celda es mayor que `0`, vuelve a su apertura. |
| 13 | `Me tienen envidia` | Copia la celda en el portapapeles. |
| 14 | `Rico, guapo y gran jugador` | Pega el portapapeles en la celda. |
| 15 | `Chilena en Turín` | Intercambia la celda y el portapapeles. |
| 16 | `Losh dosh` | Suma el portapapeles a la celda. |
| 17 | `El penalti lo tiro yo` | Si la celda vale `0`, se salta la jugada siguiente. |

La semántica exacta está en [SPEC.md §4 y §5](SPEC.md#4-semántica-de-los-comandos),
y el origen de cada frase en [§9](SPEC.md#9-origen-de-las-frases).

## Cómo se asignan valores

`Ay mi madre, el Bicho:` va seguido de una **oración**, y cada palabra de la
oración aporta una cifra: **su número de letras módulo 10**. Las cifras se leen
en orden como un número decimal.

- Solo valen las palabras de un **vocabulario cerrado** de temática Cristiano
  (clubes, compañeros, estadios, títulos…) más unos pocos conectores. La lista
  completa está en el [Anexo A de SPEC.md](SPEC.md#anexo-a-vocabulario-de-la-oración).
  Una palabra fuera de la lista es el error `E09`.
- **Casos especiales:** `7` aporta la cifra 7 (su dorsal) y `CR7` aporta la
  cifra 3 (sus tres caracteres). Son los únicos tokens con dígitos admitidos.
- **`autogol`**, como primera palabra, vuelve negativo el resultado y no aporta
  cifra.

| Oración | Cifras | Valor |
|---|---|---|
| `Cristiano Ronaldo` | 9, 7 | `97` |
| `Madridistas y portugueses` | 1 (11 letras), 1, 1 (11 letras) | `111` |
| `CR7 7` | 3, 7 | `37` |
| `autogol y` | —, 1 | `-1` |

Detalles en [SPEC.md §4.2](SPEC.md#42-ay-mi-madre-el-bicho-asignación-con-una-oración).

## Palabras prohibidas

`Messi`, `Leo`, `Lionel`, `Pulga`, `Lamine`, `Yamal`, `Mundial`, `Qatar` y
`Penaldo` no pueden aparecer en ninguna jugada, ni dentro ni fuera de una
oración, con cualquier combinación de mayúsculas y tildes. Si aparecen, el
programa no llega a ejecutarse: da el error `E13` (Roja directa) y cita la
palabra. En los comentarios sí se pueden escribir. Ver
[SPEC.md §2.6](SPEC.md#26-palabras-prohibidas).

## Instalación y uso

Hace falta Python 3.10 o posterior. El intérprete solo usa la biblioteca
estándar, así que no hay nada que instalar:

```bash
git clone <url-del-repositorio> CR7Script
```

```bash
python -m cr7script ejemplos/hola_mundo.siu
```

La entrada estándar se pasa al programa:

```bash
echo 10 | python -m cr7script ejemplos/fibonacci.siu
```

### Tests

Los tests usan `pytest`, que se instala en un entorno virtual:

```bash
python -m venv .venv
```

```bash
.venv/Scripts/python -m pip install pytest
```

```bash
.venv/Scripts/python -m pytest
```

En Linux o macOS la ruta es `.venv/bin/python`.

## Ejemplos

| Archivo | Qué hace |
|---|---|
| [`hola_mundo.siu`](ejemplos/hola_mundo.siu) | Escribe `Hola, mundo!`. |
| [`cuenta_atras.siu`](ejemplos/cuenta_atras.siu) | Lee `n` y escribe `n`, `n-1`, …, `1`, uno por línea. |
| [`sumar.siu`](ejemplos/sumar.siu) | Lee dos números, uno por línea, y escribe su suma. |
| [`eco.siu`](ejemplos/eco.siu) | Repite la entrada carácter a carácter hasta que se acaba. |
| [`fibonacci.siu`](ejemplos/fibonacci.siu) | Lee `n` y escribe los `n` primeros términos de Fibonacci. |

## Errores y códigos de salida

Los errores se escriben en la salida de errores como
`CR7Script: <código> <nombre> (jugada <n>, línea <l>): <detalle>`. Los de
análisis se detectan antes de ejecutar nada; si hay varios, se informa del
primero. Ver [SPEC.md §6](SPEC.md#6-errores).

| Código | Nombre | Cuándo |
|---|---|---|
| `E01` | Fuera de juego | Jugada que no es ningún comando. |
| `E02` | Bicho sin balón | Oración que no aporta ninguna cifra. |
| `E03` | Sin pitido inicial | No empieza por `Calma, calma, estoy aquí`, o el inicio se repite. |
| `E04` | Sin pitido final | No hay ningún `¡Siuuu!`. |
| `E05` | Partido terminado | Hay jugadas después de `¡Siuuu!`. |
| `E06` | Récord sin cerrar | Bucle sin cerrar. |
| `E07` | Récord sin perseguir | Cierre de bucle sin apertura. |
| `E08` | Comentario sin cerrar | Paréntesis sin cerrar o suelto. |
| `E09` | No convocado | Palabra de la oración fuera del vocabulario. |
| `E13` | Roja directa | Palabra prohibida. |
| `E10` | Balón fuera | Moverse a la izquierda de la primera celda. |
| `E11` | Revisión del VAR | Entrada que no es un entero o no es UTF-8 válido. |
| `E12` | Grito ininteligible | Escribir un valor que no es un carácter Unicode. |

| Código de salida | Significado |
|---|---|
| `0` | Todo bien. |
| `1` | Error de análisis (`E01`–`E09`, `E13`). |
| `2` | Error de ejecución (`E10`–`E12`). |
| `3` | Error de uso: argumentos incorrectos o archivo ilegible. |

## Créditos

CR7Script está inspirado en
[MessiScript](https://github.com/Erawaa/MessiScriptInterpreter), de Erawaa. Su
vocabulario, su forma de dar valores y sus mecánicas propias se han escrito
desde cero.

## Licencia

[MIT](LICENSE).
