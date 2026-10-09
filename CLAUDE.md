# CR7Script

Intérprete de CR7Script, un lenguaje esotérico en el que cada programa es una
jugada de Cristiano Ronaldo. Los archivos fuente usan la extensión `.siu`.

## Fuente de verdad

[SPEC.md](SPEC.md) define el lenguaje: frases, semántica, errores, códigos de
salida y ejemplos. Si el código y la spec no coinciden, la que manda es la spec.
No se inventa comportamiento que la spec no recoja: si falta algo, se añade
primero a SPEC.md.

## Tecnología

- Python 3, solo con la biblioteca estándar.
- La única dependencia externa permitida es `pytest`, y solo para los tests.

## Estructura

```
cr7script/   paquete del intérprete (se ejecuta con python -m cr7script)
tests/       tests con pytest
ejemplos/    programas .siu de ejemplo (incluidos los de SPEC.md §8)
SPEC.md      especificación del lenguaje
```

## Comandos

Ejecutar un programa (la entrada estándar se pasa al programa):

```bash
python -m cr7script ejemplos/hola_mundo.siu
```

Ejecutar todos los tests:

```bash
python -m pytest
```

Ejecutar un solo archivo de tests:

```bash
python -m pytest tests/test_errores.py -v
```

## Reglas de trabajo

- **Todo cambio de comportamiento actualiza SPEC.md y añade al menos un test**
  que lo cubra, en el mismo commit. Los cambios que no alteran el
  comportamiento (refactorizaciones, comentarios) no tocan la spec.
- Cuando se cambia la spec, se sube su número de versión.
- Los ejemplos de SPEC.md §8 existen también como archivos en `ejemplos/`, y hay
  tests que comprueban su salida exacta. Si se cambia uno, se cambia el otro.

## Errores

- Los mensajes de error van **en español** y usan los códigos y nombres de
  SPEC.md §6: `E01`–`E08` para los errores de análisis y `E10`–`E12` para los
  de ejecución. No existe `E09`.
- Formato, en la salida de errores:
  `CR7Script: <código> <nombre> (jugada <n>, línea <l>): <detalle>`
- Códigos de salida: `0` si todo va bien, `1` si hay un error de análisis y `2`
  si hay un error de ejecución.
- Los errores de análisis se detectan todos antes de ejecutar ninguna jugada.
- Cada código de error tiene al menos un test que comprueba el código, el
  mensaje y el código de salida.
