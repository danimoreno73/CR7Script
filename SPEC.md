# CR7Script — Especificación del lenguaje

**Versión:** 0.3 (borrador)
**Extensión de archivo:** `.siu`
**Codificación del código fuente:** UTF-8

CR7Script es un lenguaje esotérico en el que cada programa es una jugada de
Cristiano Ronaldo: empieza pidiendo calma, se va del Madrid y vuelve a casa,
llama al Bicho para dar valores y termina, siempre, con un `¡Siuuu!`.

Está inspirado en [MessiScript](https://github.com/Erawaa/MessiScriptInterpreter),
pero su vocabulario, su forma de dar valores y sus mecánicas propias se han
diseñado desde cero.

---

## 1. Modelo de ejecución

El estado de un programa en ejecución se compone de tres elementos:

| Elemento | Descripción | Valor inicial |
|---|---|---|
| **Campo** | Lista de enteros. Se puede ampliar sin límite por la derecha. | `[0]`, una sola celda |
| **Posición** | Índice (desde 0) de la celda actual del campo. | `0` |
| **Portapapeles** | Un entero independiente del campo. | `0` |

- Los enteros son de **precisión arbitraria**: no hay desbordamiento.
- Al moverse a la derecha más allá de la última celda, se añade una celda nueva
  con valor `0`.
- La posición nunca puede ser negativa (ver [§6](#6-errores)).
- Los comandos se ejecutan en orden, de uno en uno. Solo los bucles
  ([§4.4](#44-bucle)) y el penalti ([§5.3](#53-el-penalti-lo-tiro-yo)) alteran
  ese orden.

---

## 2. Estructura léxica

### 2.1 Jugadas (comandos)

Un programa es una secuencia de **jugadas** separadas por puntos (`.`).

1. Primero se eliminan los comentarios ([§2.3](#23-comentarios)).
2. Después el texto se divide por cada `.`.
3. A cada fragmento se le quitan los espacios del principio y del final. Los
   fragmentos vacíos se ignoran, así que da igual poner un punto después de
   `¡Siuuu!`, dejar líneas en blanco o escribir `...`.
4. Cada fragmento que queda es una jugada. Una jugada puede ocupar varias líneas.

> **Cuidado:** solo el punto separa jugadas. Los signos `!` y `?` **no**, ni
> tampoco los saltos de línea. Si una jugada acaba en `?` o `!`, necesita su
> punto igualmente: `¡Gol, gol!.` Sin él, se une a la siguiente y el resultado
> es un `E01` o, dentro de una asignación, una oración más larga de lo que se
> pretendía. Por la misma razón, `¿Eres de Málaga? Quichiano, quichiano` es
> **una sola** jugada: el `?` del medio no la corta. La única excepción es
> `¡Siuuu!`, que es la última jugada y no necesita punto.

### 2.2 Reconocimiento de frases

Para comparar una jugada con las frases del lenguaje, ambas se **normalizan**:

1. Se pasan a minúsculas.
2. Se quitan las tildes y diéresis (`á→a`, `ü→u`, `ñ→n`, etc.).
3. Se eliminan los signos `¡ ! ¿ ? , ;`.
4. Cualquier grupo de espacios, tabuladores o saltos de línea se reduce a un
   solo espacio.

Por tanto `¡AGUA!` y `agua` son la misma jugada, igual que
`eres de malaga quichiano QUICHIANO` y `¿Eres de Málaga? Quichiano, quichiano`.
Después de normalizar, la jugada debe coincidir **exactamente** con una frase:
no se admiten palabras de más ni de menos. Nunca se busca una frase *dentro* de
una jugada.

### 2.3 Comentarios

Todo lo que va entre paréntesis `( ... )` es un comentario (como el
comentarista de la tele) y se ignora. Un comentario:

- puede ocupar varias líneas y contener puntos;
- no se puede anidar: el primer `)` cierra el comentario;
- si se queda sin cerrar, o aparece un `)` suelto, es un error (`E08`).

### 2.4 Unicidad de las frases

Las frases normalizadas cumplen dos propiedades, comprobadas automáticamente
contra la tabla de [§3](#3-tabla-de-comandos):

1. **Ninguna frase es prefijo de otra**, ni carácter a carácter ni palabra a
   palabra. Para `¡Siuuu!` se comprueba la forma mínima `siuuu` y, además, que
   ninguna otra frase se ajuste a `^siu{3,}$`. Para la asignación se usa la parte
   anterior a los dos puntos, `ay mi madre el bicho`.
2. **Ninguna frase contiene `:`**, así que una jugada con dos puntos solo puede
   ser una asignación.

Gracias a esto, un intérprete puede reconocer las frases con una tabla de
búsqueda exacta o con un árbol de prefijos sin ambigüedad.

Forma normalizada de cada frase:

| Frase | Forma normalizada |
|---|---|
| `Calma, calma, estoy aquí` | `calma calma estoy aqui` |
| `¡Siuuu!` | `siuuu` (o más `u`) |
| `Fue muy bonito estar en el Madrid` | `fue muy bonito estar en el madrid` |
| `He vuelto a casa` | `he vuelto a casa` |
| `Ay mi madre, el Bicho:` | `ay mi madre el bicho` |
| `Agua` | `agua` |
| `Soy el primero, el segundo y el tercero` | `soy el primero el segundo y el tercero` |
| `¿Eres de Málaga? Quichiano, quichiano` | `eres de malaga quichiano quichiano` |
| `Más un poco y estás aquí, madre mía hijo mío` | `mas un poco y estas aqui madre mia hijo mio` |
| `Anda a patear, muestra personalidad` | `anda a patear muestra personalidad` |
| `Yo no persigo los récords` | `yo no persigo los records` |
| `Los récords me persiguen a mí` | `los records me persiguen a mi` |
| `Me tienen envidia` | `me tienen envidia` |
| `Rico, guapo y gran jugador` | `rico guapo y gran jugador` |
| `Chilena en Turín` | `chilena en turin` |
| `Losh dosh` | `losh dosh` |
| `El penalti lo tiro yo` | `el penalti lo tiro yo` |

### 2.5 `Agua` dentro de una oración

`Agua` es la frase más corta del lenguaje, pero no puede activarse por
accidente dentro de una asignación:

- Una asignación es **una sola jugada**. Todo lo que va detrás de sus dos puntos
  es oración, y en la oración cada palabra solo cuenta letras. Así,
  `Ay mi madre, el Bicho: agua` asigna `4` y **no** pone la celda a cero.
- Una jugada solo es `Agua` si, normalizada, es exactamente `agua`. `Agua fría`
  o `Agua: algo` son `E01`.
- La única forma de que `Agua` se mezcle con una oración es olvidar el punto que
  las separa (ver el aviso de [§2.1](#21-jugadas-comandos)):
  `Ay mi madre, el Bicho: Siempre yo` + salto de línea + `Agua.` es **una**
  jugada con la oración `Siempre yo Agua`, que vale `724`.

---

## 3. Tabla de comandos

| # | Frase | Acción |
|---|---|---|
| 1 | `Calma, calma, estoy aquí` | **Inicio** del programa. |
| 2 | `¡Siuuu!` | **Fin** del programa. Lleva tres `u` o más. |
| 3 | `Fue muy bonito estar en el Madrid` | Posición + 1 (derecha). |
| 4 | `He vuelto a casa` | Posición − 1 (izquierda). |
| 5 | `Ay mi madre, el Bicho: <oración>` | **Asigna** a la celda actual el valor de la oración ([§4.2](#42-ay-mi-madre-el-bicho-asignación-con-una-oración)). |
| 6 | `Agua` | Pone la celda actual a `0`. |
| 7 | `Soy el primero, el segundo y el tercero` | Escribe la celda actual como número decimal. |
| 8 | `¿Eres de Málaga? Quichiano, quichiano` | Escribe el carácter Unicode cuyo código es la celda actual. |
| 9 | `Más un poco y estás aquí, madre mía hijo mío` | Lee un número entero y lo guarda en la celda actual. |
| 10 | `Anda a patear, muestra personalidad` | Lee un carácter y guarda su código Unicode en la celda actual. |
| 11 | `Yo no persigo los récords` | **Abre** un bucle. |
| 12 | `Los récords me persiguen a mí` | **Cierra** un bucle. |
| 13 | `Me tienen envidia` | **Copia**: portapapeles ← celda actual. |
| 14 | `Rico, guapo y gran jugador` | **Pega**: celda actual ← portapapeles. |
| 15 | `Chilena en Turín` | *Propia:* intercambia la celda actual y el portapapeles. |
| 16 | `Losh dosh` | *Propia:* celda actual ← celda actual + portapapeles. |
| 17 | `El penalti lo tiro yo` | *Propia:* si la celda actual es `0`, se salta la jugada siguiente. |

Los comandos 15, 16 y 17 no existen en MessiScript (ver [§5](#5-mecánicas-propias)).
El origen de cada frase está en [§9](#9-origen-de-las-frases).

---

## 4. Semántica de los comandos

### 4.1 Inicio y fin

- La **primera** jugada de todo programa tiene que ser `Calma, calma, estoy aquí`,
  y no puede volver a aparecer.
- La **última** jugada tiene que ser `¡Siuuu!`. Tras normalizar, la jugada debe
  ajustarse a la expresión regular `^siu{3,}$`, así que `¡Siuuu!`,
  `¡SIUUUUUUU!` y `siuuuu` valen, pero `¡Siu!` no.
- Después de `¡Siuuu!` no puede haber más jugadas (solo comentarios y espacios).
- Al llegar a `¡Siuuu!` el programa termina con código de salida `0`. No se
  escribe nada automáticamente (ni siquiera un salto de línea).

### 4.2 Ay mi madre, el Bicho: asignación con una oración

```
Ay mi madre, el Bicho: <oración>
```

La jugada se parte por el **primer** `:`. La parte de la izquierda, normalizada,
tiene que ser `ay mi madre el bicho`. La parte de la derecha es la **oración**.

El valor de la oración se calcula **contando letras**: cada palabra aporta una
cifra decimal, que es su número de letras módulo 10.

1. La oración se divide en palabras por los espacios en blanco.
2. De cada palabra se cuentan solo las **letras** (caracteres Unicode de la
   categoría `L`, tras normalizar a NFC). Tildes y eñes cuentan como una letra:
   `Turín` tiene 5. Los signos, dígitos y guiones no cuentan: `hat-trick` tiene 8.
3. Las palabras con 0 letras (`¡`, `—`, `7`…) se ignoran por completo.
4. Cada palabra restante aporta la cifra `letras mod 10`:

   | Letras | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | … |
   |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
   | Cifra | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 | 1 | 2 | … |

5. Las cifras, en orden, se leen como un número decimal. Los ceros a la izquierda
   no importan.
6. **Autogol:** si la primera palabra (normalizada) es `autogol`, no aporta
   ninguna cifra y el resultado es **negativo**.
7. El resultado **sustituye** al valor de la celda actual (no se suma).

Las palabras de la oración nunca se interpretan como comandos, aunque
coincidan con uno (ver [§2.5](#25-agua-dentro-de-una-oración)).

Si la oración no tiene ninguna palabra que aporte cifra (está vacía, o solo
contiene `autogol`), es un error de análisis (`E02`).

La oración no puede contener puntos, que separan jugadas, ni paréntesis, que
abren comentarios.

**Ejemplos:**

| Jugada | Letras por palabra | Valor |
|---|---|---|
| `Ay mi madre, el Bicho: Cristiano Ronaldo` | 9, 7 | `97` |
| `Ay mi madre, el Bicho: Siempre yo` | 7, 2 | `72` |
| `Ay mi madre, el Bicho: A Portuguesa` | 1, 10 | `10` |
| `Ay mi madre, el Bicho: ¡Gol, gol!` | 3, 3 | `33` |
| `Ay mi madre, el Bicho: Madridistas y portugueses` | 11, 1, 11 | `111` |
| `Ay mi madre, el Bicho: agua` | 4 | `4` |
| `Ay mi madre, el Bicho: autogol y` | — , 1 | `-1` |
| `Ay mi madre, el Bicho: Portuguesa` | 10 | `0` |

### 4.3 Entrada y salida

**`Soy el primero, el segundo y el tercero`**: escribe en la salida estándar la
representación decimal de la celda actual, con un `-` delante si es negativa.
No añade espacios ni saltos de línea.

**`¿Eres de Málaga? Quichiano, quichiano`**: escribe el carácter Unicode cuyo
código es el valor de la celda actual, codificado en UTF-8. El valor tiene que
estar entre `0` y `0x10FFFF`, sin ser un sustituto (`0xD800`–`0xDFFF`). Si no lo
está, es el error `E12`.

**`Más un poco y estás aquí, madre mía hijo mío`**: lee **una línea** de la
entrada estándar (sin el salto de línea final), le quita los espacios de los
extremos y la interpreta como entero según `^[+-]?[0-9]+$`. Si la línea no se
ajusta a ese formato, o la entrada ya ha terminado (EOF), es el error `E11`.
La línea completa queda consumida.

**`Anda a patear, muestra personalidad`**: lee **un carácter** Unicode (UTF-8) de la
entrada estándar y guarda su código en la celda actual. El salto de línea
también es un carácter (`10`). Si la entrada ha terminado (EOF), guarda `0`; eso
no es un error. Si los bytes no forman UTF-8 válido, es el error `E11`.

### 4.4 Bucle

```
Yo no persigo los récords.
    ...cuerpo...
Los récords me persiguen a mí.
```

- **`Yo no persigo los récords`**: si la celda actual vale `0`, salta a la
  jugada siguiente a su `Los récords me persiguen a mí` emparejado. Si no, sigue
  con normalidad.
- **`Los récords me persiguen a mí`**: si la celda actual **no** vale `0`,
  vuelve a la jugada siguiente a su `Yo no persigo los récords` emparejado. Si
  vale `0`, sigue.

Los bucles se pueden anidar. La pareja de cada apertura y cada cierre se
calcula una sola vez, **antes** de ejecutar nada. Un bucle sin cerrar (`E06`) o
un cierre sin apertura (`E07`) impiden que el programa arranque.

### 4.5 Copiar, pegar y poner a cero

- **`Me tienen envidia`**: copia la celda actual en el portapapeles. La celda
  no cambia.
- **`Rico, guapo y gran jugador`**: copia el portapapeles en la celda actual.
  El portapapeles no cambia.
- **`Agua`**: pone la celda actual a `0`. El portapapeles no cambia.

### 4.6 Movimiento

- **`Fue muy bonito estar en el Madrid`**: posición + 1. Si es necesario, el
  campo crece con una celda a `0`.
- **`He vuelto a casa`**: posición − 1. Si la posición ya es `0`, es el error
  `E10` y el programa se detiene.

---

## 5. Mecánicas propias

Estas tres mecánicas no existen en MessiScript.

### 5.1 `Chilena en Turín`: intercambio

Intercambia el valor de la celda actual y el del portapapeles en un solo paso
(como la chilena de 2018 en Turín, que lo puso todo del revés). Sirve para
guardar un valor y recuperar otro sin gastar celdas.

```
(celda = 5, portapapeles = 9)
Chilena en Turín.
(celda = 9, portapapeles = 5)
```

### 5.2 `Losh dosh`: suma

Suma el portapapeles a la celda actual (los dos valores juntos):
`celda ← celda + portapapeles`. El portapapeles no cambia. Junto con `autogol`
es la única forma de restar:

```
Ay mi madre, el Bicho: autogol y.     (celda = -1)
Me tienen envidia.                    (portapapeles = -1)
Ay mi madre, el Bicho: Siempre yo.    (celda = 72)
Losh dosh.                            (celda = 71)
```

### 5.3 `El penalti lo tiro yo`: salto condicional

Si la celda actual vale `0`, el penalti se falla y la **jugada siguiente no se
ejecuta**. Si vale otra cosa, se marca y la ejecución sigue con normalidad.

- La jugada saltada se omite sea cual sea, incluidos los bucles: si se salta un
  `Yo no persigo los récords`, se entra en el cuerpo sin comprobar la condición;
  si se salta un `Los récords me persiguen a mí`, se sale del bucle sin volver
  atrás. Las parejas de los bucles no cambian, porque se calcularon antes de
  ejecutar.
- Si la jugada siguiente es `¡Siuuu!`, saltarla equivale a terminar: el programa
  acaba igualmente con código `0`.
- Varios penaltis seguidos: un penalti fallado se salta solo la jugada
  siguiente, aunque esa jugada sea otro penalti.

---

## 6. Errores

Todos los errores se escriben en la **salida de errores** con este formato:

```
CR7Script: <código> <nombre> (jugada <n>, línea <l>): <detalle>
```

`<n>` es el número de la jugada (empezando por 1) y `<l>` la línea del archivo
donde empieza. Si el error no corresponde a ninguna jugada (por ejemplo, un
comentario sin cerrar), se indica solo la línea.

### 6.1 Errores de análisis: el partido no empieza

Se detectan **antes de ejecutar ninguna jugada**. Si hay alguno, el programa no
produce ninguna salida, se informa del **primero** que aparece en el archivo y
el código de salida es `1`.

| Código | Nombre | Cuándo ocurre |
|---|---|---|
| `E01` | Fuera de juego | **Comando desconocido:** la jugada no coincide con ninguna frase, o tiene un `:` y lo que va delante no es `ay mi madre el bicho`. |
| `E02` | Bicho sin balón | La oración de una asignación no aporta ninguna cifra. |
| `E03` | Sin pitido inicial | La primera jugada no es `Calma, calma, estoy aquí`, el archivo está vacío o la frase de inicio aparece otra vez más adelante. |
| `E04` | Sin pitido final | El programa no termina con `¡Siuuu!`. |
| `E05` | Partido terminado | Hay jugadas después de `¡Siuuu!`. |
| `E06` | Récord sin cerrar | **Bucle sin cerrar:** un `Yo no persigo los récords` no tiene su `Los récords me persiguen a mí`. |
| `E07` | Récord sin perseguir | Un `Los récords me persiguen a mí` no tiene ningún `Yo no persigo los récords` abierto. |
| `E08` | Comentario sin cerrar | Falta un `)`, o hay un `)` sin su `(`. |

### 6.2 Errores de ejecución: tarjeta roja

Detienen el programa en el momento en que ocurren. Lo que ya se haya escrito en
la salida estándar se mantiene. El código de salida es `2`.

| Código | Nombre | Cuándo ocurre |
|---|---|---|
| `E10` | Balón fuera | **Posición negativa:** `He vuelto a casa` con la posición en `0`. |
| `E11` | Revisión del VAR | **Entrada no válida:** `Más un poco y estás aquí, madre mía hijo mío` recibe algo que no es un entero o se encuentra el EOF, o `Anda a patear, muestra personalidad` recibe UTF-8 no válido. |
| `E12` | Grito ininteligible | `¿Eres de Málaga? Quichiano, quichiano` con un valor que no es un código Unicode válido. |

### 6.3 Códigos de salida

| Código | Significado |
|---|---|
| `0` | El programa llegó a `¡Siuuu!` (o lo saltó con un penalti). |
| `1` | Error de análisis (`E01`–`E08`). |
| `2` | Error de ejecución (`E10`–`E12`). |

---

## 7. Gramática

Notación EBNF. Se aplica al texto **sin comentarios** y con cada jugada ya
normalizada según [§2.2](#22-reconocimiento-de-frases), excepto la oración,
que conserva su texto original para contar letras.

```ebnf
programa    = inicio , "." , { jugada , "." } , fin , [ "." ] ;
inicio      = "calma calma estoy aqui" ;
fin         = "si" , "u" , "u" , "u" , { "u" } ;
jugada      = movimiento | asignacion | simple | bucle ;
movimiento  = "fue muy bonito estar en el madrid" | "he vuelto a casa" ;
asignacion  = "ay mi madre el bicho" , ":" , oracion ;
simple      = "agua"
            | "soy el primero el segundo y el tercero"
            | "eres de malaga quichiano quichiano"
            | "mas un poco y estas aqui madre mia hijo mio"
            | "anda a patear muestra personalidad"
            | "me tienen envidia" | "rico guapo y gran jugador"
            | "chilena en turin" | "losh dosh"
            | "el penalti lo tiro yo" ;
bucle       = "yo no persigo los records" , "." , { jugada , "." } ,
              "los records me persiguen a mi" ;
oracion     = [ "autogol" ] , palabra , { palabra } ;   (* al menos una palabra con letras *)
```

Los fragmentos vacíos entre puntos no aparecen en la gramática porque se
eliminan antes ([§2.1](#21-jugadas-comandos)).

---

## 8. Ejemplos

### 8.1 Hola mundo

Escribe `Hola, mundo!` seguido de un salto de línea. Todo ocurre en la celda
`0`: en cada paso el Bicho pone el código del carácter y `¿Eres de Málaga?
Quichiano, quichiano` lo escribe. La `o` (111) se guarda en el portapapeles la
primera vez y se pega la segunda.

Archivo `hola_mundo.siu`:

```
Calma, calma, estoy aquí.

(H = 72)
Ay mi madre, el Bicho: Siempre yo.
¿Eres de Málaga? Quichiano, quichiano.

(o = 111; la guardamos para después)
Ay mi madre, el Bicho: Madridistas y portugueses.
¿Eres de Málaga? Quichiano, quichiano.
Me tienen envidia.

(l = 108)
Ay mi madre, el Bicho: Y Manchester, Juventus.
¿Eres de Málaga? Quichiano, quichiano.

(a = 97)
Ay mi madre, el Bicho: Cristiano Ronaldo.
¿Eres de Málaga? Quichiano, quichiano.

(coma = 44)
Ay mi madre, el Bicho: Pura gana.
¿Eres de Málaga? Quichiano, quichiano.

(espacio = 32)
Ay mi madre, el Bicho: Soy yo.
¿Eres de Málaga? Quichiano, quichiano.

(m = 109)
Ay mi madre, el Bicho: Y Manchester, Champions.
¿Eres de Málaga? Quichiano, quichiano.

(u = 117)
Ay mi madre, el Bicho: Madridistas y Ronaldo.
¿Eres de Málaga? Quichiano, quichiano.

(n = 110)
Ay mi madre, el Bicho: Portugueses y goleadores.
¿Eres de Málaga? Quichiano, quichiano.

(d = 100)
Ay mi madre, el Bicho: Inigualable, goleadores, campeonato.
¿Eres de Málaga? Quichiano, quichiano.

(o = 111, sale del portapapeles)
Rico, guapo y gran jugador.
¿Eres de Málaga? Quichiano, quichiano.

(exclamación = 33)
Ay mi madre, el Bicho: ¡Gol, gol!.
¿Eres de Málaga? Quichiano, quichiano.

(salto de línea = 10)
Ay mi madre, el Bicho: A Portuguesa.
¿Eres de Málaga? Quichiano, quichiano.

¡Siuuu!
```

Comprobación de las oraciones:

| Carácter | Oración | Letras | Valor |
|---|---|---|---|
| `H` | Siempre yo | 7, 2 | 72 |
| `o` | Madridistas y portugueses | 11, 1, 11 | 111 |
| `l` | Y Manchester, Juventus | 1, 10, 8 | 108 |
| `a` | Cristiano Ronaldo | 9, 7 | 97 |
| `,` | Pura gana | 4, 4 | 44 |
| ` ` | Soy yo | 3, 2 | 32 |
| `m` | Y Manchester, Champions | 1, 10, 9 | 109 |
| `u` | Madridistas y Ronaldo | 11, 1, 7 | 117 |
| `n` | Portugueses y goleadores | 11, 1, 10 | 110 |
| `d` | Inigualable, goleadores, campeonato | 11, 10, 10 | 100 |
| `!` | ¡Gol, gol! | 3, 3 | 33 |
| `\n` | A Portuguesa | 1, 10 | 10 |

### 8.2 Cuenta atrás (bucle y mecánicas propias)

Lee un número `n` y escribe `n`, `n-1`, …, `1`, uno por línea. Usa la celda `0`
como contador y la `1` para el salto de línea. Si `n` es `0`, no escribe nada.
Si `n` es negativo, el bucle no termina nunca.

```
Calma, calma, estoy aquí.

(portapapeles = -1)
Ay mi madre, el Bicho: autogol y.
Me tienen envidia.

(celda 0 = n)
Más un poco y estás aquí, madre mía hijo mío.

Yo no persigo los récords.
    Soy el primero, el segundo y el tercero.
    Fue muy bonito estar en el Madrid.
    Ay mi madre, el Bicho: A Portuguesa.
    ¿Eres de Málaga? Quichiano, quichiano.
    He vuelto a casa.
    Losh dosh.                          (n = n - 1)
Los récords me persiguen a mí.

¡Siuuu!
```

Con la entrada `3` escribe:

```
3
2
1
```

---

## 9. Origen de las frases

**Verificada** significa que hay prensa que recoge la frase o el momento.
**Parcial** significa que el momento es real, pero la frase del lenguaje es
una adaptación o no se ha encontrado con esa redacción exacta. **Sin fuente**
significa que no se ha encontrado una fuente publicada.

| Frase | Comando | Origen | Estado |
|---|---|---|---|
| `Calma, calma, estoy aquí` | Inicio | Celebración de su gol del 1-2 en el Camp Nou (Liga, 21 de abril de 2012): pidió calma a la grada y se señaló el pecho. La prensa lo recoge como «Calma, calma, que estoy aquí». Retomaba un gesto de Raúl. | Verificada |
| `¡Siuuu!` | Fin | Su grito de celebración. Según él, salió espontáneamente en un amistoso de pretemporada contra el Chelsea en Estados Unidos (2013), y se popularizó en la gala del Balón de Oro 2014. Viene del «sí» en español. | Verificada |
| `Fue muy bonito estar en el Madrid` | Mover a la derecha | Tras ganar la final de la Champions en Kiev (26 de mayo de 2018), anticipando su salida. La cita original dice «en el **Real** Madrid». | Verificada (adaptada) |
| `He vuelto a casa` | Mover a la izquierda | Su regreso al Manchester United en agosto de 2021, que la prensa tituló como «vuelve a casa». No se ha encontrado la cita textual en español. | Parcial |
| `Ay mi madre, el Bicho` | Asignar | «El Bicho» es su apodo, popularizado por el narrador Manolo Lama en la COPE. No se ha encontrado la exclamación completa. | Parcial |
| `Agua` | Poner a cero | Rueda de prensa previa al Portugal–Hungría de la Euro 2020 (Budapest, junio de 2021): apartó dos botellas de Coca-Cola y levantó una de agua. | Verificada |
| `Soy el primero, el segundo y el tercero` | Mostrar número | — | Sin fuente |
| `¿Eres de Málaga? Quichiano, quichiano` | Mostrar carácter | — | Sin fuente |
| `Más un poco y estás aquí, madre mía hijo mío` | Leer número | — | Sin fuente |
| `Anda a patear, muestra personalidad` | Leer carácter | Adaptación al español de lo que le dijo a João Moutinho, que dudaba si lanzar, antes de la tanda de penaltis contra Polonia (cuartos de la Euro 2016, Marsella, 30 de junio de 2016). El original es en portugués. El momento está grabado y documentado; la redacción exacta del original no se ha contrastado. | Parcial (adaptada) |
| `Yo no persigo los récords` | Abrir bucle | Idea que ha repetido varias veces, con distintas redacciones: «no los busco, los récords me buscan a mí» (2019, tras su gol 700); «Yo no busco los récords, los récords me buscan a mí» (antes del Mundial 2022); «No persigo los récords, ellos me persiguen a mí» (en redes, en la liga saudí). | Parcial |
| `Los récords me persiguen a mí` | Cerrar bucle | Segunda mitad de la misma frase. | Parcial |
| `Me tienen envidia` | Copiar | Tras el Dinamo de Zagreb–Real Madrid de la Champions (septiembre de 2011), explicó los silbidos: «soy rico, guapo y un gran jugador. Me tienen envidia». | Verificada |
| `Rico, guapo y gran jugador` | Pegar | La misma declaración. La cita dice «un gran jugador». | Verificada (adaptada) |
| `Chilena en Turín` | Intercambiar | No es una cita: alude a su gol de chilena ante la Juventus en Turín (cuartos de la Champions, 3 de abril de 2018). | Referencia |
| `Losh dosh` | Sumar portapapeles | — | Sin fuente |
| `El penalti lo tiro yo` | Penalti | No es una cita: frase creada para CR7Script, por ser el lanzador habitual de penaltis de sus equipos. | Inventada |
