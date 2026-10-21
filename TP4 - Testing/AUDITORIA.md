# AUDITORIA.md


## Sección 1: Los tests de la IA (`test_checkout_ia.py`)

### 1. Clasificación individual de los 8 tests

1. `test_subtotal`: **Tautológico**. Recrea el cálculo del subtotal multiplicando por el catálogo de producción (`CATALOGO["buzo"] * 2`) en el propio `assert`. Si el precio del catálogo o el cálculo están mal en producción, el test sigue pasando.
2. `test_total_funciona`: **Débil**. Solo comprueba `assert resultado is not None`. Cualquier objeto o diccionario devuelto (incluso con importes en cero o erróneos) aprueba la aserción.
3. `test_total_positivo`: **Débil**. Se limita a verificar `assert resultado["total"] > 0`. Aprueba cualquier total mayor a cero sin validar la exactitud de los importes o del cálculo numérico.
4. `test_cupon_egresados`: **Tautológico**. El valor esperado replica la fórmula matemática (`100000 * 0.15`) directamente en la aserción en vez de comparar contra una constante concreta calculada a mano.
5. `test_envio_caba`: **Útil**. Invoca `calcular_envio(10000, "CABA")` y compara contra el valor numérico constante esperado (`2500`).
6. `test_descuento_por_cantidad`: **Útil**. Compara el resultado de `calcular_descuento(100000, 6, None, date(2026, 10, 1))` contra la constante absoluta esperada (`10000`).
7. `test_talle_valido`: **Inútil**. Llama a `validar_item(...)` sin ningún `assert`. No verifica valores de retorno ni mutaciones de estado; solo detectaría excepciones no capturadas.
8. `test_no_explota_con_varios_productos`: **Inútil**. Envuelve la llamada a `calcular_total` en un bloque `try ... except Exception: pass` que silencia cualquier falla, haciendo que el test siempre dé verde.

---

### 2. Puntaje de mutación

- **Puntaje de mutación obtenido:** `58.6%` (17 mutantes muertos de 29 generados; 12 mutantes sobrevivientes).

---

### 3. Explicación: ¿Por qué cubre casi el 80% del código y no detecta fallas?

La cobertura de código (por ejemplo, ~80%) únicamente mide qué líneas de código fueron ejecutadas por el intérprete de Python durante la corrida de tests, pero no evalúa la calidad ni la corrección de los resultados. La suite de la IA pasa por casi todas las líneas del backend, pero no detecta fallas de negocio por los siguientes tres problemas principales:

1. **Falta de oráculos / aserciones inútiles:** Tests como `test_talle_valido` no incluyen aserciones o, como `test_no_explota_con_varios_productos`, capturan y suprimen todas las excepciones con `except Exception: pass`.
2. **Aserciones permisivas y débiles:** Tests como `test_total_funciona` o `test_total_positivo` se conforman con verificar que la respuesta no sea nula o que el total sea mayor a 0, ignorando si el precio devuelto viola las reglas de negocio.
3. **Lógica tautológica:** Al recalcular el valor esperado en el `assert` usando los mismos datos o fórmulas del módulo bajo prueba (`CATALOGO["buzo"] * 2`), cualquier error de lógica o de datos se enmascara automáticamente.

---

## Sección 2: Hallazgos

### 1. Resultado del linter (`ruff check checkout.py`)

- **Resultado:** `All checks passed!`
- *Observación:* El linter estático no detecta fallas de lógica de negocio, violaciones del contrato de especificación, errores en límites numéricos ni imprecisiones de punto flotante en operaciones monetarias.

---

### 2 y 3. Detalle de fallas encontradas en los módulos

#### Hallazgo H-01
- **Archivo y línea:** `checkout.py`, líneas 62 y 64
- **Categoría:** Efectos laterales / Lógica
- **Regla de la especificación:** R4 ("Ninguna función modifica el carrito que recibe")
- **Cómo se encontró:** Lectura de código y caso de caja negra de R4.
- **Severidad:** Media.
- **Descripción:** `validar_item` muta directamente el diccionario recibido (`item["talle"] = item["talle"].upper()`), alterando la estructura enviada por el cliente.

#### Hallazgo H-02
- **Archivo y línea:** `checkout.py`, línea 67
- **Categoría:** Lógica y límites
- **Regla de la especificación:** R3 (Cantidad válida entre 1 y 10, ambos inclusive)
- **Cómo se encontró:** Análisis de valores límite (caja negra).
- **Severidad:** Media.
- **Descripción:** La condición `not (1 <= item["cantidad"] < 10)` rechaza la cantidad límite 10 al usar `< 10` en vez de `<= 10`.

#### Hallazgo H-03
- **Archivo y línea:** `checkout.py`, líneas 75-76
- **Categoría:** Manejo de errores
- **Regla de la especificación:** R1 ("Un producto que no está en el catálogo → PRODUCTO_INEXISTENTE")
- **Cómo se encontró:** Lectura del bloque `try ... except` en `calcular_subtotal`.
- **Severidad:** Alta.
- **Descripción:** Un bloque `except:` silencioso en `calcular_subtotal` ignora la excepción cuando un producto no existe en el catálogo y saltea el ítem con `continue` en lugar de lanzar `CheckoutError("PRODUCTO_INEXISTENTE", ...)`.

#### Hallazgo H-04
- **Archivo y línea:** `checkout.py`, línea 73
- **Categoría:** Seguridad / Lógica
- **Regla de la especificación:** R1 ("El precio sale siempre del catálogo. Si el ítem trae un precio propio, se ignora")
- **Cómo se encontró:** Lectura de código.
- **Severidad:** Alta.
- **Descripción:** `calcular_subtotal` hace `item.get("precio", CATALOGO[...])`, priorizando la clave `precio` del usuario si viene en el JSON, lo que permite alterar los precios desde el frontend.

#### Hallazgo H-05
- **Archivo y línea:** `checkout.py`, línea 82
- **Categoría:** Lógica y límites
- **Regla de la especificación:** R5 ("Si la cantidad total de prendas ... es 5 o más, se aplica un 10%")
- **Cómo se encontró:** Valores límite en caja negra.
- **Severidad:** Media.
- **Descripción:** La condición `if cantidad_prendas > 5:` excluye la compra de exactamente 5 prendas. Debería ser `>= 5`.

#### Hallazgo H-06
- **Archivo y línea:** `checkout.py`, línea 85
- **Categoría:** Fechas
- **Regla de la especificación:** R6 ("Si no se recibe fecha, se usa la fecha del día en que se hace la llamada")
- **Cómo se encontró:** Inspección de la firma de `calcular_descuento`.
- **Severidad:** Media.
- **Descripción:** Utiliza `fecha=date.today()` como argumento por defecto en la definición de la función. En Python, esto evalúa la fecha una sola vez cuando se importa el módulo y no en cada llamada a la función.

#### Hallazgo H-07
- **Archivo y línea:** `checkout.py`, línea 97
- **Categoría:** Fechas / Límites
- **Regla de la especificación:** R6 ("EGRESADOS2026: Válido hasta el 30/11/2026 inclusive")
- **Cómo se encontró:** Casos límite con fechas en caja negra.
- **Severidad:** Media.
- **Descripción:** La validación `if not fecha < datos["vence"]:` considera vencido al cupón en la misma fecha de vencimiento (`30/11/2026`). La condición adecuada es `fecha > datos["vence"]`.

#### Hallazgo H-08
- **Archivo y línea:** `checkout.py`, línea 88
- **Categoría:** Strings
- **Regla de la especificación:** R6 ("No se distingue mayúscula de minúscula y se ignoran los espacios")
- **Cómo se encontró:** Pruebas de caja negra con cupones en minúscula.
- **Severidad:** Baja.
- **Descripción:** `codigo = cupon.strip()` quita espacios laterales pero no aplica `.upper()`, rechazando cupones válidos ingresados en minúsculas (ej: `"egresados2026"`).

#### Hallazgo H-09
- **Archivo y línea:** `checkout.py`, líneas 22, 90 y 117
- **Categoría:** Numéricos / Tipos
- **Regla de la especificación:** R7 ("Todos los importes se manejan como Decimal. Nunca float")
- **Cómo se encontró:** Inspección de tipos devueltos e importaciones.
- **Severidad:** Alta.
- **Descripción:** El módulo define los precios y porcentajes como floats (`24999.90`, `0.15`), usa `round()` estándar y devuelve tipos `float` en lugar de `Decimal`, provocando imprecisiones monetarias de punto flotante.

#### Hallazgo H-10
- **Archivo y línea:** `checkout.py`, línea 23
- **Categoría:** Alucinación / Code smell
- **Regla de la especificación:** R6 ("Estos son los únicos dos cupones que existen")
- **Cómo se encontró:** Lectura de la constante `CUPONES`.
- **Severidad:** Media.
- **Descripción:** Incluye el cupón no especificado `"DEBUG100"` con 100% de descuento vencible en el año 2099.

#### Hallazgo H-11
- **Archivo y línea:** `checkout.py`, línea 121
- **Categoría:** Alucinación / Métodos
- **Regla de la especificación:** R8 (Manejo de errores en zonas)
- **Cómo se encontró:** Lectura de la función `calcular_envio`.
- **Severidad:** Alta.
- **Descripción:** Llama a `ENVIOS.keys().join(', ')`, pero la vista `dict_keys` de Python no posee el método `join`, produciendo un `AttributeError` no capturado al intentar formatear la excepción.

#### Hallazgo H-12
- **Archivo y línea:** `pedidos.py`, línea 42
- **Categoría:** Manejo de errores / Transacciones
- **Regla de la especificación:** R10 ("Si un pedido falla no debe guardarse nada: ni el pedido ni sus ítems")
- **Cómo se encontró:** Análisis del flujo de la función `guardar_pedido`.
- **Severidad:** Alta.
- **Descripción:** `guardar_pedido` ejecuta un `INSERT` en `pedidos` y realiza un `con.commit()` *antes* de llamar a `calcular_total`. Si `calcular_total` lanza un `CheckoutError`, el registro parcial ya quedó asentado en la base de datos.

#### Hallazgo H-13
- **Archivo y línea:** `pedidos.py`, línea 100
- **Categoría:** Seguridad
- **Regla de la especificación:** R10 (Búsqueda parametrizada e inalterable)
- **Cómo se encontró:** Lectura de la consulta en `pedidos_de`.
- **Severidad:** Alta.
- **Descripción:** Construye la sentencia SQL interpolando directamente la cadena con f-strings (`SELECT id FROM pedidos WHERE email = '{email}'`), lo que expone el sistema a inyecciones SQL.

#### Hallazgo H-14
- **Archivo y línea:** `api.py`, líneas 55 y 67
- **Categoría:** Manejo de errores / Contrato HTTP
- **Regla de la especificación:** R11 ("Un error nunca puede devolver 500 ... CheckoutError debe devolver 422")
- **Cómo se encontró:** Lectura de las respuestas en los métodos `do_POST` y `do_GET`.
- **Severidad:** Alta.
- **Descripción:** Los bloques `except Exception as e:` capturan todos los errores (incluidos los `CheckoutError`) y devuelven HTTP 500 con un formato plano `{"error": str(e)}` en lugar de responder con los códigos HTTP 400/422 y la estructura JSON requerida.

---

### 4. Tabla de fallas ordenadas por severidad

| Archivo | Línea | Categoría | Regla Violada | Descripción Breve | Severidad |
|---|---|---|---|---|---|
| `checkout.py` | 73 | Seguridad / Lógica | R1 | Toma el `precio` enviado en el ítem del cliente en vez del `CATALOGO` | **Alta** |
| `checkout.py` | 75 | Manejo de errores | R1 | Ignora excepciones con `except:` en lugar de lanzar `PRODUCTO_INEXISTENTE` | **Alta** |
| `checkout.py` | 22, 90 | Numéricos / Tipos | R7 | Utiliza `float` en lugar de `Decimal` para los montos | **Alta** |
| `checkout.py` | 121 | Alucinación | R8 | Invocación del método inexistente `keys().join()` | **Alta** |
| `pedidos.py` | 42 | Transacciones | R10 | Commit prematuro en SQLite antes de verificar el checkout | **Alta** |
| `pedidos.py` | 100 | Seguridad | R10 | Inyección SQL por interpolación de cadenas mediante f-strings | **Alta** |
| `api.py` | 55, 67 | Manejo de errores | R11 | Responde HTTP 500 para errores de negocio y validación | **Alta** |
| `checkout.py` | 67 | Lógica y límites | R3 | La condición `< 10` rechaza la cantidad válida 10 | **Media** |
| `checkout.py` | 82 | Lógica y límites | R5 | La condición `> 5` no incluye las 5 prendas para el descuento | **Media** |
| `checkout.py` | 85 | Fechas | R6 | Uso de `fecha=date.today()` como argumento por defecto | **Media** |
| `checkout.py` | 97 | Fechas / Límites | R6 | Invalida cupones en su mismo día de vencimiento | **Media** |
| `checkout.py` | 62 | Efectos laterales | R4 | `validar_item` muta el diccionario `item` recibido | **Media** |
| `checkout.py` | 23 | Alucinación / Code smell | R6 | Incluye el cupón no autorizado `DEBUG100` | **Media** |
| `checkout.py` | 88 | Strings | R6 | No convierte a mayúsculas (`.upper()`) el código de cupón | **Baja** |
