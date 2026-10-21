## Cómo leer las tablas

- **Partición:** clase de equivalencia (**V** = válida, **I** = inválida).
- **Límites:** el valor de borde que se prueba (un valor de cada lado del corte).
- **Caso:** la entrada. `item(producto, talle, cantidad)` es un ítem del carrito.
  Los importes son `Decimal`.
- **Esperado:** el resultado o el `code` del `CheckoutError`.
- **Nivel:** unitario (R1–R9), integración (R10) o E2E (R11).

Precios: buzo 24.999,90 · remera 11.999,50 · campera 47.999,99.

## Interpretaciones adoptadas (donde la especificación no es explícita)

| # | Tema | Decisión |
|---|------|----------|
| 1 | Cantidad (R3) | `True` y `2.0` son `CANTIDAD_INVALIDA`: solo un entero puro entre 1 y 10 es válido. |
| 2 | Tipos raros | Talle que no es texto → `TALLE_INVALIDO`. Producto faltante o que no es texto → `PRODUCTO_INEXISTENTE`. Cupón que no es texto → `CUPON_INVALIDO`. Carrito que no es lista → `CARRITO_VACIO`. |
| 3 | Cupón contra R5 | Un cupón inválido, vencido o bajo el mínimo lanza su error aunque R5 dé más descuento. |
| 4 | API | `cupon` que no es texto → 400 `DATOS_INCOMPLETOS`. PUT y DELETE no se prueban. |
| 5 | API | `GET /api/v1/pedidos/abc` → 404 `RUTA_INEXISTENTE`. |
| 6 | Por analogía con 2 | `talle` faltante → `TALLE_INVALIDO`. `cantidad` faltante → `CANTIDAD_INVALIDA`. |
| 7 | Por analogía con R11 | Un cuerpo JSON que no es un objeto (por ejemplo `[]`) → 400 `DATOS_INCOMPLETOS`. Una `fecha` que no es texto → 400 `FECHA_INVALIDA`. |

---

## R1 — Catálogo y precios

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: buzo | — | `calcular_subtotal([item("buzo","M",1)])` | `24999.90` | Unitario |
| V: remera | — | `calcular_subtotal([item("remera","M",1)])` | `11999.50` | Unitario |
| V: campera | — | `calcular_subtotal([item("campera","M",1)])` | `47999.99` | Unitario |
| V: varios productos | — | buzo×1 + remera×2 + campera×1 | `96998.89` | Unitario |
| V: mismo producto en dos ítems | — | `item("buzo","M",1)` + `item("buzo","L",2)` | `74999.70` | Unitario |
| V: el precio sale del catálogo | precio propio menor | `item("buzo","M",1, precio=1)` | `24999.90` (el precio del ítem se ignora) | Unitario |
| V: el precio sale del catálogo | precio propio mayor | `item("buzo","M",1, precio=99999)` | `24999.90` | Unitario |
| V: clave extra ignorada | — | `item("buzo","M",1, color="rojo")` | `24999.90`, sin error | Unitario |
| I: mayúscula | `buzo` / `Buzo` | `validar_item(item("Buzo","M",1))` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: todo en mayúscula | — | `validar_item(item("BUZO","M",1))` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: espacio al principio | — | `validar_item(item(" buzo","M",1))` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: espacio al final | — | `validar_item(item("buzo ","M",1))` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: plural parecido | — | `validar_item(item("buzos","M",1))` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: no está en el catálogo | — | `validar_item(item("pantalon","M",1))` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: vacío | — | `validar_item(item("","M",1))` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: sin la clave `producto` | — | `validar_item({"talle":"M","cantidad":1})` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: no es texto | `None` | `validar_item(item(None,"M",1))` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: no es texto | número | `validar_item(item(5,"M",1))` | `PRODUCTO_INEXISTENTE` | Unitario |
| I: inexistente dentro de `calcular_total` | — | `calcular_total([item("pantalon","M",1)], "CABA")` | `PRODUCTO_INEXISTENTE` | Unitario |

## R2 — Talles

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: cada talle del conjunto | `XS`, `S`, `M`, `L`, `XL`, `XXL` | `validar_item(item("buzo", t, 1))` para cada `t` | no lanza error, devuelve `None` | Unitario |
| V: minúscula | — | talle `"m"` | válido | Unitario |
| V: minúscula (dos letras) | — | talle `"xl"` | válido | Unitario |
| V: mayúscula y minúscula mezcladas | — | talle `"xXl"` | válido | Unitario |
| V: espacios alrededor | — | talle `"  M "` | válido | Unitario |
| V: espacios solo al final | — | talle `"XL  "` | válido | Unitario |
| I: fuera del conjunto | primer valor fuera | talle `"XXXL"` | `TALLE_INVALIDO` | Unitario |
| I: numérico | — | talle `"42"` | `TALLE_INVALIDO` | Unitario |
| I: parecido a uno válido | — | talle `"MM"` | `TALLE_INVALIDO` | Unitario |
| I: parecido a uno válido | — | talle `"2XL"` | `TALLE_INVALIDO` | Unitario |
| I: espacio interno | — | talle `"X L"` | `TALLE_INVALIDO` | Unitario |
| I: dos talles juntos | — | talle `"M L"` | `TALLE_INVALIDO` | Unitario |
| I: vacío | — | talle `""` | `TALLE_INVALIDO` | Unitario |
| I: solo espacios | — | talle `"   "` | `TALLE_INVALIDO` | Unitario |
| I: no es texto | `None` | talle `None` | `TALLE_INVALIDO` | Unitario |
| I: no es texto | número | talle `5` | `TALLE_INVALIDO` | Unitario |
| I (\*): sin la clave `talle` | — | `{"producto":"buzo","cantidad":1}` | `TALLE_INVALIDO` | Unitario |

## R3 — Cantidad

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: entero dentro del rango | límite inferior | cantidad `1` | válida | Unitario |
| V: entero dentro del rango | valor intermedio | cantidad `5` | válida | Unitario |
| V: entero dentro del rango | justo debajo del tope | cantidad `9` | válida | Unitario |
| V: entero dentro del rango | límite superior (inclusive) | cantidad `10` | válida | Unitario |
| I: por debajo del rango | justo debajo del mínimo | cantidad `0` | `CANTIDAD_INVALIDA` | Unitario |
| I: por debajo del rango | negativo | cantidad `-1` | `CANTIDAD_INVALIDA` | Unitario |
| I: por encima del rango | justo encima del tope | cantidad `11` | `CANTIDAD_INVALIDA` | Unitario |
| I: por encima del rango | muy grande | cantidad `100` | `CANTIDAD_INVALIDA` | Unitario |
| I: no entero (decimal) | — | cantidad `1.5` | `CANTIDAD_INVALIDA` | Unitario |
| I: no entero (decimal) | dentro del rango | cantidad `2.5` | `CANTIDAD_INVALIDA` | Unitario |
| I: decimal con valor entero | — | cantidad `2.0` | `CANTIDAD_INVALIDA` | Unitario |
| I: booleano | `True` | cantidad `True` | `CANTIDAD_INVALIDA` | Unitario |
| I: texto | — | cantidad `"3"` | `CANTIDAD_INVALIDA` | Unitario |
| I: sin valor | `None` | cantidad `None` | `CANTIDAD_INVALIDA` | Unitario |
| I (\*): sin la clave `cantidad` | — | `{"producto":"buzo","talle":"M"}` | `CANTIDAD_INVALIDA` | Unitario |
| I: dentro de `calcular_total` | — | `calcular_total([item("buzo","M",11)], "CABA")` | `CANTIDAD_INVALIDA` | Unitario |

## R4 — Carrito

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| I: carrito vacío | 0 ítems | `calcular_total([], "CABA")` | `CARRITO_VACIO` | Unitario |
| I: carrito vacío | 0 ítems | `calcular_subtotal([])` | `CARRITO_VACIO` | Unitario |
| I: no es lista | `None` | `calcular_total(None, "CABA")` | `CARRITO_VACIO` | Unitario |
| V: un ítem | mínimo permitido (1 ítem) | `calcular_total([item("buzo","M",1)], "CABA")` | sin error | Unitario |
| V: varios ítems | — | tres ítems válidos | sin error | Unitario |
| No modifica el carrito | `calcular_total` | carrito con talle `"  m "` y clave extra: `deepcopy` antes y después de llamar | el carrito es idéntico al original (talle sigue `"  m "`) | Unitario |
| No modifica el carrito | `calcular_subtotal` | mismo carrito, `deepcopy` antes y después | idéntico | Unitario |
| No modifica el carrito | `validar_item` | ítem con talle `"  m "`, `deepcopy` antes y después | el ítem sigue con `"  m "` | Unitario |
| No modifica el carrito | llamada que falla | carrito con ítem 1 válido e ítem 2 con talle inválido: `deepcopy` antes y después | idéntico, aunque lance `TALLE_INVALIDO` | Unitario |
| No modifica el carrito | se puede reutilizar | llamar dos veces a `calcular_total` con el mismo carrito | las dos veces da el mismo resultado | Unitario |

## R5 — Descuento por cantidad

Se prueba con `calcular_descuento(subtotal, cantidad_prendas)` y, para la suma de
cantidades, con `calcular_total`.

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: sin descuento | 1 prenda | `calcular_descuento(100000, 1)` | `0.00` | Unitario |
| V: sin descuento | 4 prendas (justo debajo del corte) | `calcular_descuento(100000, 4)` | `0.00` | Unitario |
| V: con descuento | 5 prendas (el corte, inclusive) | `calcular_descuento(100000, 5)` | `10000.00` | Unitario |
| V: con descuento | 6 prendas | `calcular_descuento(100000, 6)` | `10000.00` | Unitario |
| V: con descuento | 10 prendas | `calcular_descuento(100000, 10)` | `10000.00` | Unitario |
| V: el porcentaje es el 10 % | otro subtotal | `calcular_descuento(250000, 5)` | `25000.00` | Unitario |
| V: redondeo del 10 % (mitad) | 10,005 | `calcular_descuento(100.05, 5)` | `10.01` | Unitario |
| V: redondeo del 10 % (debajo de la mitad) | 10,004 | `calcular_descuento(100.04, 5)` | `10.00` | Unitario |
| V: cuenta la suma de ítems | 4 prendas en 2 ítems | buzo×2 + remera×2, CABA | subtotal `73998.80`, descuento `0.00`, envío `0.00`, total `73998.80` | Unitario |
| V: cuenta la suma de ítems | 5 prendas en 2 ítems (corte) | buzo×2 + remera×3, CABA | subtotal `85998.30`, descuento `8599.83`, envío `0.00`, total `77398.47` | Unitario |
| V: 5 prendas, un solo ítem | corte, envío con descuento < 60.000 | remera×5, CABA | subtotal `59997.50`, descuento `5999.75`, envío `2500.00`, total `56497.75` | Unitario |
| V: 4 prendas, un solo ítem | justo debajo del corte | remera×4, CABA | subtotal `47998.00`, descuento `0.00`, envío `2500.00`, total `50498.00` | Unitario |
| V: el descuento es sobre el subtotal | no incluye el envío | remera×5, GBA | descuento `5999.75` (10 % del subtotal, no del total) | Unitario |

## R6 — Cupones

### `EGRESADOS2026` (15 %, válido hasta el 30/11/2026 inclusive)

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: vigente | muy anterior | `calcular_descuento(100000, 1, "EGRESADOS2026", 2026-10-01)` | `15000.00` | Unitario |
| V: vigente | un día antes del vencimiento | fecha `2026-11-29` | `15000.00` | Unitario |
| V: vigente | último día (inclusive) | fecha `2026-11-30` | `15000.00` | Unitario |
| I: vencido | primer día vencido | fecha `2026-12-01` | `CUPON_VENCIDO` | Unitario |
| I: vencido | un año después | fecha `2027-11-30` | `CUPON_VENCIDO` | Unitario |
| V: redondeo de la mitad | 1.799,925 | `calcular_descuento(11999.50, 1, "EGRESADOS2026", 2026-11-30)` | `1799.93` | Unitario |

### `BIENVENIDA` ($ 3.000, subtotal mínimo de $ 20.000)

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| I: bajo el mínimo | un centavo debajo | `calcular_descuento(19999.99, 1, "BIENVENIDA", 2026-10-01)` | `CUPON_MINIMO_NO_ALCANZADO` | Unitario |
| V: mínimo alcanzado | exactamente el mínimo | subtotal `20000.00` | `3000.00` | Unitario |
| V: mínimo alcanzado | un centavo encima | subtotal `20000.01` | `3000.00` | Unitario |
| V: monto fijo, no porcentual | subtotal grande | subtotal `100000.00` | `3000.00` | Unitario |
| V: no tiene fecha de vencimiento | mucho tiempo después | fecha `2030-01-01`, subtotal `20000.00` | `3000.00` | Unitario |
| V: no tiene fecha de vencimiento | día posterior al de `EGRESADOS2026` | fecha `2026-12-01`, subtotal `20000.00` | `3000.00` | Unitario |

### Normalización del código

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: minúscula | — | `"egresados2026"` (subtotal 100000, 1 prenda, fecha vigente) | `15000.00` | Unitario |
| V: mezcla de mayúsculas | — | `"Egresados2026"` | `15000.00` | Unitario |
| V: espacios alrededor | — | `"  EGRESADOS2026 "` | `15000.00` | Unitario |
| V: minúscula | — | `"bienvenida"` (subtotal 20000) | `3000.00` | Unitario |
| V: espacios alrededor | — | `" BIENVENIDA  "` (subtotal 20000) | `3000.00` | Unitario |

### Sin cupón

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: `None` | — | `calcular_descuento(100000, 1, None, fecha)` | `0.00`, sin error | Unitario |
| V: texto vacío | — | cupón `""` | `0.00`, sin error | Unitario |
| V: solo espacios | — | cupón `"   "` | `0.00`, sin error | Unitario |
| V: sin cupón pero con R5 | cupón vacío y 5 prendas | `calcular_descuento(100000, 5, "", fecha)` | `10000.00` (el cupón vacío no pisa a R5) | Unitario |
| V: sin cupón en `calcular_total` | — | `calcular_total([item("buzo","M",1)], "CABA", "  ")` | sin error | Unitario |

### Cupón inexistente

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| I: no existe | — | `"DESCUENTO50"` | `CUPON_INVALIDO` | Unitario |
| I: «los únicos dos cupones que existen» | cupón no listado | `"DEBUG100"` | `CUPON_INVALIDO` | Unitario |
| I: parecido al válido | año distinto | `"EGRESADOS2025"` | `CUPON_INVALIDO` | Unitario |
| I: parecido al válido | espacio interno | `"EGRESADOS 2026"` | `CUPON_INVALIDO` | Unitario |
| I: parecido al válido | caracteres de más | `"EGRESADOS2026X"` | `CUPON_INVALIDO` | Unitario |
| I: no es texto | número | cupón `123` | `CUPON_INVALIDO` | Unitario |

### No se acumula con R5 (se aplica el mayor)

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: gana el cupón porcentual | 15 % > 10 % | `calcular_descuento(100000, 5, "EGRESADOS2026", fecha vigente)` | `15000.00` (no `25000.00`) | Unitario |
| V: gana R5 | 10 % > $ 3.000 | `calcular_descuento(100000, 5, "BIENVENIDA", fecha)` | `10000.00` (no `13000.00`) | Unitario |
| V: gana el cupón fijo | $ 3.000 > 10 % | `calcular_descuento(20000, 5, "BIENVENIDA", fecha)` | `3000.00` (10 % sería `2000.00`) | Unitario |
| V: empate | $ 3.000 = 10 % | `calcular_descuento(30000, 5, "BIENVENIDA", fecha)` | `3000.00` | Unitario |
| V: menos de 5 prendas | R5 no aplica | `calcular_descuento(100000, 4, "BIENVENIDA", fecha)` | `3000.00` | Unitario |
| I: cupón inválido aunque R5 sea mayor | — | `calcular_descuento(100000, 5, "NOEXISTE", fecha)` | `CUPON_INVALIDO` | Unitario |
| I: cupón vencido aunque R5 sea mayor | — | `calcular_descuento(100000, 5, "EGRESADOS2026", 2026-12-01)` | `CUPON_VENCIDO` | Unitario |
| I: mínimo no alcanzado aunque R5 sea mayor | — | `calcular_descuento(19999.99, 5, "BIENVENIDA", fecha)` | `CUPON_MINIMO_NO_ALCANZADO` | Unitario |

### Tope y fecha por defecto

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: invariante «el descuento no supera el subtotal» | subtotal mínimo del cupón fijo | `calcular_descuento(20000, 1, "BIENVENIDA", fecha)` | `3000.00`, que es menor o igual al subtotal | Unitario |
| V: sin fecha, se usa hoy | hoy = `2026-11-30` (simulado) | `calcular_descuento(100000, 1, "EGRESADOS2026")` | `15000.00` | Unitario |
| I: sin fecha, se usa hoy | hoy = `2026-12-01` (simulado) | `calcular_descuento(100000, 1, "EGRESADOS2026")` | `CUPON_VENCIDO` | Unitario |
| I: la fecha de hoy se evalúa en cada llamada | hoy cambia entre dos llamadas | primera llamada con hoy `2026-11-30`, segunda con hoy `2026-12-01` | la primera da `15000.00`, la segunda `CUPON_VENCIDO` | Unitario |
| I: lo mismo en `calcular_total` | hoy = `2026-12-01` (simulado) | `calcular_total([item("buzo","M",1)], "CABA", "EGRESADOS2026")` | `CUPON_VENCIDO` | Unitario |

## R7 — Dinero y redondeo

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: redondeo de la mitad hacia arriba | 1.799,925 (ejemplo de la spec) | 15 % de `11999.50` | `1799.93` | Unitario |
| V: redondeo de la mitad hacia arriba | 3.749,985 | 15 % de `24999.90` | `3749.99` | Unitario |
| V: debajo de la mitad | 15,0045 | 15 % de `100.03` | `15.00` | Unitario |
| V: encima de la mitad | 15,006 | 15 % de `100.04` | `15.01` | Unitario |
| V: sin pérdida de precisión | tres buzos | `calcular_subtotal([item("buzo","M",3)])` | exactamente `Decimal("74999.70")` | Unitario |
| V: sin pérdida de precisión | tres remeras | remera×3 | exactamente `Decimal("35998.50")` | Unitario |
| V: sin pérdida de precisión | tres camperas | campera×3 | exactamente `Decimal("143999.97")` | Unitario |
| V: sin pérdida de precisión | tope de cantidad | buzo×10 | exactamente `Decimal("249999.00")` | Unitario |
| V: tipo de `calcular_subtotal` | — | `calcular_subtotal(carrito válido)` | es `Decimal`, no `float` ni `int` | Unitario |
| V: tipo de `calcular_descuento` | con cupón | resultado de `calcular_descuento` | es `Decimal` | Unitario |
| V: tipo de `calcular_descuento` | sin descuento | resultado cuando no hay descuento | es `Decimal("0.00")`, no el entero `0` | Unitario |
| V: tipo de `calcular_envio` | zona con costo | resultado de `calcular_envio` | es `Decimal` | Unitario |
| V: tipo de `calcular_envio` | envío gratis | resultado de `calcular_envio` | es `Decimal`, no el entero `0` | Unitario |
| V: tipos de `calcular_total` | — | `calcular_total(...)` | devuelve un `dict` con exactamente las claves `subtotal`, `descuento`, `envio` y `total`, todas `Decimal` | Unitario |
| V: valores exactos al centavo | ejemplo de la spec | `calcular_total([item("buzo","M",2)], "CABA")` | `Decimal("49999.80")`, `Decimal("0.00")`, `Decimal("2500.00")` y `Decimal("52499.80")` | Unitario |

## R8 — Envío

`calcular_envio(subtotal_con_descuento, zona)`

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: CABA | — | `calcular_envio(10000, "CABA")` | `2500.00` | Unitario |
| V: GBA | — | `calcular_envio(10000, "GBA")` | `4000.00` | Unitario |
| V: INTERIOR | — | `calcular_envio(10000, "INTERIOR")` | `6500.00` | Unitario |
| V: RETIRO | — | `calcular_envio(10000, "RETIRO")` | `0.00` | Unitario |
| V: normalización | minúscula | `"caba"` | `2500.00` | Unitario |
| V: normalización | espacios alrededor | `"  GBA "` | `4000.00` | Unitario |
| V: normalización | mezcla de mayúsculas | `"Interior"` | `6500.00` | Unitario |
| V: normalización | minúscula y espacios | `"  retiro  "` | `0.00` | Unitario |
| V: sin envío gratis | un centavo debajo del corte | `calcular_envio(59999.99, "CABA")` | `2500.00` | Unitario |
| V: sin envío gratis | un centavo debajo del corte | `calcular_envio(59999.99, "INTERIOR")` | `6500.00` | Unitario |
| V: envío gratis | exactamente el corte (inclusive) | `calcular_envio(60000.00, "CABA")` | `0.00` | Unitario |
| V: envío gratis | un centavo encima | `calcular_envio(60000.01, "GBA")` | `0.00` | Unitario |
| V: envío gratis en cualquier zona | subtotal grande | `calcular_envio(100000, "INTERIOR")` | `0.00` | Unitario |
| V: el corte mira el subtotal ya con descuento | subtotal ≥ 60.000 pero con descuento < 60.000 | 2 buzos + 1 remera (subtotal `61999.30`), cupón `EGRESADOS2026` (fecha vigente), CABA | subtotal `61999.30`, descuento `9299.90`, envío `2500.00`, total `55199.40` | Unitario |
| V: contraste sin cupón | mismo carrito, sin descuento | 2 buzos + 1 remera, sin cupón, CABA | subtotal `61999.30`, descuento `0.00`, envío `0.00`, total `61999.30` | Unitario |
| I: zona que no existe | — | `calcular_envio(10000, "NORTE")` | `ZONA_INVALIDA` | Unitario |
| I: zona que no existe | nombre largo | `"BUENOS AIRES"` | `ZONA_INVALIDA` | Unitario |
| I: vacía | — | `""` | `ZONA_INVALIDA` | Unitario |
| I: solo espacios | — | `"   "` | `ZONA_INVALIDA` | Unitario |
| I: aunque el envío sea gratis | subtotal ≥ 60.000 | `calcular_envio(70000, "NORTE")` | `ZONA_INVALIDA` | Unitario |

## R9 — Total

`total = subtotal − descuento + envío`

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: ejemplo de la spec | sin descuento | 2 buzos M, CABA, sin cupón | subtotal `49999.80`, descuento `0.00`, envío `2500.00`, total `52499.80` | Unitario |
| V: con cupón porcentual | ejemplo del R11 | remera×1, CABA, `EGRESADOS2026`, fecha `2026-11-30` | subtotal `11999.50`, descuento `1799.93`, envío `2500.00`, total `12699.57` | Unitario |
| V: con cupón fijo | — | buzo×1, CABA, `BIENVENIDA`, fecha `2026-10-01` | subtotal `24999.90`, descuento `3000.00`, envío `2500.00`, total `24499.90` | Unitario |
| V: envío gratis, sin descuento | — | campera×2, GBA, sin cupón | subtotal `95999.98`, descuento `0.00`, envío `0.00`, total `95999.98` | Unitario |
| V: R5 y envío gratis | — | buzo×5, INTERIOR, sin cupón | subtotal `124999.50`, descuento `12499.95`, envío `0.00`, total `112499.55` | Unitario |
| V: gana el cupón sobre R5 | — | buzo×5, CABA, `EGRESADOS2026`, fecha `2026-10-01` | subtotal `124999.50`, descuento `18749.93`, envío `0.00`, total `106249.57` | Unitario |
| V: retiro en el colegio | envío 0 | buzo×1, RETIRO, sin cupón | subtotal `24999.90`, descuento `0.00`, envío `0.00`, total `24999.90` | Unitario |
| V: la fecha se pasa a los cupones | — | remera×1, CABA, `EGRESADOS2026`, fecha `2026-12-01` | `CUPON_VENCIDO` | Unitario |

## Sección 3 — Orden de validación en `calcular_total`

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| Carrito vacío primero | contra todo lo demás | `calcular_total([], "NORTE", "NOEXISTE")` | `CARRITO_VACIO` | Unitario |
| Dentro del ítem: producto antes que talle | — | `item("pantalon","XXXL",1)` | `PRODUCTO_INEXISTENTE` | Unitario |
| Dentro del ítem: producto antes que cantidad | — | `item("pantalon","M",0)` | `PRODUCTO_INEXISTENTE` | Unitario |
| Dentro del ítem: talle antes que cantidad | — | `item("buzo","XXXL",0)` | `TALLE_INVALIDO` | Unitario |
| Dentro del ítem: los tres inválidos | — | `item("pantalon","XXXL",0)` | `PRODUCTO_INEXISTENTE` | Unitario |
| Entre ítems: gana el primero | error distinto en cada uno | ítem 1 con talle inválido, ítem 2 con producto inexistente | `TALLE_INVALIDO` | Unitario |
| Entre ítems: gana el primero | el primero válido | ítem 1 válido, ítem 2 con cantidad inválida, ítem 3 con producto inexistente | `CANTIDAD_INVALIDA` | Unitario |
| Ítem antes que cupón | — | ítem con talle inválido y cupón `"NOEXISTE"` | `TALLE_INVALIDO` | Unitario |
| Cupón antes que zona | — | cupón `"NOEXISTE"` y zona `"NORTE"` | `CUPON_INVALIDO` | Unitario |
| Cupón vencido antes que zona | — | `EGRESADOS2026` fecha `2026-12-01` y zona `"NORTE"` | `CUPON_VENCIDO` | Unitario |
| Zona al final | todo lo demás válido | zona `"NORTE"` | `ZONA_INVALIDA` | Unitario |

## Sección 1 y 4 — Contrato de `CheckoutError`

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| `CheckoutError` expone los dos atributos | — | capturar el error de `TALLE_INVALIDO` | `error.code == "TALLE_INVALIDO"` y `error.mensaje` es un texto no vacío | Unitario |
| Cada código de la tabla de errores | los 8 códigos | provocar cada uno (`PRODUCTO_INEXISTENTE`, `TALLE_INVALIDO`, `CANTIDAD_INVALIDA`, `CARRITO_VACIO`, `CUPON_INVALIDO`, `CUPON_VENCIDO`, `CUPON_MINIMO_NO_ALCANZADO`, `ZONA_INVALIDA`) | el `code` es exactamente el de la tabla | Unitario |
| Nunca otra excepción | datos raros | `calcular_total(None, "CABA")`, ítem con talle `None`, ítem con producto `None`, cupón `123` | siempre `CheckoutError`, nunca `TypeError`, `KeyError` ni `AttributeError` | Unitario |

---

## R10 — Persistencia (`pedidos.py`)

### Errores de negocio: no queda nada guardado

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| I: carrito vacío | 0 ítems | `guardar_pedido(con, email, [], "CABA")` | lanza `CheckoutError` con `CARRITO_VACIO`; 0 filas en `pedidos` y 0 en `items` (verificado desde otra conexión) | Integración |
| I: talle inválido en el ítem 2 | ítem 1 válido | carrito con dos ítems, el segundo con talle `"XXXL"` | `TALLE_INVALIDO`; 0 filas en `pedidos` y 0 en `items` | Integración |
| I: cupón inexistente | — | cupón `"NOEXISTE"` | `CUPON_INVALIDO`; 0 filas en `pedidos` y 0 en `items` | Integración |
| I: cupón vencido | `fecha` pasada a `guardar_pedido` | `EGRESADOS2026` con fecha `2026-12-01` | `CUPON_VENCIDO`; 0 filas | Integración |
| I: zona inexistente | — | zona `"NORTE"` | `ZONA_INVALIDA`; 0 filas | Integración |
| I: error después de un pedido válido | ya hay 1 pedido | guardar un pedido válido y luego uno inválido | queda exactamente 1 pedido y sus ítems; el inválido no deja nada | Integración |

### El pedido es definitivo

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: lo ve otra conexión | un ítem | `guardar_pedido` y leer con una segunda conexión a la misma base | `obtener_pedido` con la otra conexión devuelve el pedido completo | Integración |
| V: lo ve otra conexión, con todos los ítems | varios ítems | pedido de 3 ítems, leído desde otra conexión | los 3 ítems están presentes | Integración |
| V: el id devuelto es válido | — | el id de `guardar_pedido` | es un entero y `obtener_pedido` con ese id devuelve ese pedido | Integración |

### Los montos son idénticos a los de `checkout`

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: ejemplo de la spec | — | remera×1, CABA, `EGRESADOS2026`, fecha `2026-11-30` | `subtotal == Decimal("11999.50")`, `descuento == Decimal("1799.93")`, `envio == Decimal("2500.00")`, `total == Decimal("12699.57")` | Integración |
| V: son `Decimal` | — | los cuatro montos de `obtener_pedido` | son `Decimal`, no `float` | Integración |
| V: sin pérdida de precisión | importe que no es exacto en `float` | buzo×3, CABA | `subtotal == Decimal("74999.70")` | Integración |
| V: coinciden con `calcular_total` | — | comparar `obtener_pedido` con `calcular_total` del mismo carrito | los cuatro montos son iguales | Integración |
| V: el precio unitario es `Decimal` | — | `precio_unitario` de cada ítem | es `Decimal` con el valor exacto del catálogo | Integración |

### Precio del catálogo

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: precio enviado por el cliente | precio menor | `item("buzo","M",1, precio=1)` | `precio_unitario == Decimal("24999.90")` y subtotal `24999.90` | Integración |
| V: precio enviado por el cliente | precio mayor | `item("remera","M",1, precio=99999)` | `precio_unitario == Decimal("11999.50")` | Integración |
| V: sin precio del cliente | — | `item("campera","M",1)` | `precio_unitario == Decimal("47999.99")` | Integración |

### Normalización de datos

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: email | mayúsculas y espacios | `"  Ana@Mail.COM "` | se guarda `"ana@mail.com"` | Integración |
| V: zona | minúscula y espacios | `" caba "` | se guarda `"CABA"` | Integración |
| V: talle | minúscula y espacios | `" m "` | el ítem se guarda con talle `"M"` | Integración |
| V: cupón | minúscula y espacios | `" egresados2026 "` (fecha vigente) | se guarda `"EGRESADOS2026"` | Integración |
| V: cupón vacío | `""` | cupón `""` | se guarda `None` | Integración |
| V: cupón de solo espacios | `"   "` | cupón `"   "` | se guarda `None` | Integración |
| V: sin cupón | `None` | cupón `None` | se guarda `None` | Integración |

### Lectura

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| I: id inexistente | base vacía | `obtener_pedido(con, 999)` | `None` | Integración |
| I: id inexistente | con pedidos guardados | un id mayor que el último | `None` | Integración |
| I: id inexistente | cero | `obtener_pedido(con, 0)` | `None` | Integración |
| I: id inexistente | negativo | `obtener_pedido(con, -1)` | `None` | Integración |
| V: formato del pedido | — | `obtener_pedido` de un pedido de 2 ítems | claves `id`, `email`, `zona`, `cupon`, `subtotal`, `descuento`, `envio`, `total`, `items`; cada ítem con `producto`, `talle`, `cantidad`, `precio_unitario` | Integración |
| V: orden de los ítems | — | pedido con ítems buzo, remera, campera | los ítems vuelven en el orden en que se enviaron | Integración |
| V: pedidos independientes | — | guardar dos pedidos distintos | cada uno conserva solo sus ítems | Integración |

### `pedidos_de`

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: email con pedidos | — | un pedido de `ana@mail.com` | `pedidos_de(con, "ana@mail.com")` devuelve 1 pedido | Integración |
| V: sin pedidos | — | `pedidos_de(con, "nadie@mail.com")` | `[]` | Integración |
| V: no distingue mayúsculas | — | pedido de `ana@mail.com`, consulta `"ANA@MAIL.COM"` | devuelve el pedido | Integración |
| V: no distingue espacios | — | consulta `"  ana@mail.com "` | devuelve el pedido | Integración |
| V: orden del más reciente al más antiguo | 3 pedidos | tres pedidos del mismo email, guardados en orden 1, 2, 3 | la lista viene con los ids en orden 3, 2, 1 | Integración |
| V: solo los del email consultado | dos emails | pedidos de `ana@mail.com` y de `bruno@mail.com` | cada consulta devuelve solo los suyos | Integración |
| V: apóstrofe en el email | dato legítimo | email `"o'brien@mail.com"` guardado y consultado | devuelve su pedido, sin error | Integración |
| I: inyección SQL (condición siempre verdadera) | — | consulta con `"' OR '1'='1"` habiendo pedidos de otros | `[]`: no devuelve pedidos ajenos | Integración |
| I: inyección SQL (consulta extra) | — | consulta con `"x'; DROP TABLE pedidos; --"` | `[]` y la tabla `pedidos` sigue existiendo con sus filas | Integración |
| I: inyección SQL (comentario) | — | consulta con `"ana@mail.com' --"` | `[]`, no devuelve los pedidos de `ana@mail.com` | Integración |

---

## R11 — API HTTP (`api.py`)

### `POST /api/v1/pedidos` — creación

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: pedido completo | ejemplo de la spec | email, zona `CABA`, remera×1, cupón `EGRESADOS2026`, fecha `"2026-11-30"` | 201 con `{"id": <int>, "subtotal": "11999.50", "descuento": "1799.93", "envio": "2500.00", "total": "12699.57"}` | E2E |
| V: sin `cupon` ni `fecha` | opcionales | email, zona `CABA`, buzo×1 | 201 con subtotal `"24999.90"`, descuento `"0.00"`, envío `"2500.00"`, total `"27499.90"` | E2E |
| V: los montos viajan como texto | — | respuesta de cualquier 201 | `subtotal`, `descuento`, `envio` y `total` son `str`, nunca número | E2E |
| V: cupón en minúscula | — | cupón `"bienvenida"`, buzo×1 | 201 con descuento `"3000.00"` | E2E |
| V: el ítem lleva un precio propio | — | `{"producto":"buzo","talle":"M","cantidad":1,"precio":1}` | 201 con subtotal `"24999.90"` | E2E |
| V: ids distintos | dos pedidos | crear dos pedidos seguidos | los dos ids son distintos | E2E |

### `GET /api/v1/pedidos/{id}` — consulta

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| V: pedido existente | — | crear un pedido y pedirlo por su id | 200 con el pedido completo (sección 6): `id`, `email`, `zona`, `cupon`, `subtotal`, `descuento`, `envio`, `total`, `items` | E2E |
| V: los montos viajan como texto | — | `GET` del pedido de `EGRESADOS2026` | `descuento == "1799.93"`, `total == "12699.57"` y el `precio_unitario` de cada ítem como texto | E2E |
| V: lo guardado coincide con lo enviado | normalización | crear con email `"  Ana@Mail.COM "`, zona `" caba "`, talle `" m "` | el `GET` devuelve `"ana@mail.com"`, `"CABA"` y talle `"M"` | E2E |
| V: cupón sin usar | — | crear sin cupón y pedirlo | `cupon` es `null` | E2E |
| V: varios ítems | — | pedido con 2 ítems | el `GET` devuelve los 2, en orden | E2E |

### Errores de negocio (422)

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| I: producto inexistente | — | ítem con `producto` `"pantalon"` | 422, `error.code == "PRODUCTO_INEXISTENTE"` | E2E |
| I: talle inválido | ejemplo de la spec | talle `"XXXL"` | 422, `error.code == "TALLE_INVALIDO"` y `error.message` es un texto no vacío | E2E |
| I: cantidad inválida | 11 | cantidad `11` | 422, `CANTIDAD_INVALIDA` | E2E |
| I: carrito vacío | `[]` | `"carrito": []` | 422, `CARRITO_VACIO` | E2E |
| I: cupón inexistente | — | cupón `"NOEXISTE"` | 422, `CUPON_INVALIDO` | E2E |
| I: cupón vencido | fecha `"2026-12-01"` | `EGRESADOS2026` con esa fecha | 422, `CUPON_VENCIDO` | E2E |
| I: mínimo del cupón no alcanzado | subtotal bajo el mínimo | remera×1 con `BIENVENIDA` (subtotal `11999.50`) | 422, `CUPON_MINIMO_NO_ALCANZADO` | E2E |
| I: zona inexistente | — | zona `"NORTE"` | 422, `ZONA_INVALIDA` | E2E |
| I: no queda nada guardado | — | un 422 y luego `GET` del id que habría correspondido | 404 `PEDIDO_INEXISTENTE` | E2E |

### Errores del cuerpo (400)

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| I: no es JSON | texto suelto | cuerpo `no es json` | 400, `JSON_INVALIDO` | E2E |
| I: JSON incompleto | llave sin cerrar | cuerpo `{"email": ` | 400, `JSON_INVALIDO` | E2E |
| I: cuerpo vacío | 0 bytes | `POST` sin cuerpo | 400, `JSON_INVALIDO` | E2E |
| I: falta `email` | — | cuerpo sin `email` | 400, `DATOS_INCOMPLETOS` | E2E |
| I: falta `zona` | — | cuerpo sin `zona` | 400, `DATOS_INCOMPLETOS` | E2E |
| I: falta `carrito` | — | cuerpo sin `carrito` | 400, `DATOS_INCOMPLETOS` | E2E |
| I: `email` de otro tipo | número | `"email": 123` | 400, `DATOS_INCOMPLETOS` | E2E |
| I: `zona` de otro tipo | lista | `"zona": ["CABA"]` | 400, `DATOS_INCOMPLETOS` | E2E |
| I: `carrito` de otro tipo | texto | `"carrito": "buzo"` | 400, `DATOS_INCOMPLETOS` | E2E |
| I: `carrito` de otro tipo | objeto | `"carrito": {"producto": "buzo"}` | 400, `DATOS_INCOMPLETOS` | E2E |
| I: `cupon` de otro tipo | número | `"cupon": 123` | 400, `DATOS_INCOMPLETOS` | E2E |
| I (\*): el cuerpo no es un objeto | lista | cuerpo `[]` | 400, `DATOS_INCOMPLETOS` | E2E |
| I: fecha con otro formato | `DD/MM/AAAA` | `"fecha": "30/11/2026"` | 400, `FECHA_INVALIDA` | E2E |
| I: fecha que no existe | mes 13 | `"fecha": "2026-13-01"` | 400, `FECHA_INVALIDA` | E2E |
| I: fecha que no existe | 30 de febrero | `"fecha": "2026-02-30"` | 400, `FECHA_INVALIDA` | E2E |
| I: fecha que no es una fecha | texto | `"fecha": "hoy"` | 400, `FECHA_INVALIDA` | E2E |
| I (\*): fecha de otro tipo | número | `"fecha": 20261130` | 400, `FECHA_INVALIDA` | E2E |
| V: fecha válida en el límite | último día de `EGRESADOS2026` | `"fecha": "2026-11-30"` con `EGRESADOS2026` | 201 | E2E |

### Errores 404

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| I: pedido inexistente | id grande | `GET /api/v1/pedidos/999` | 404, `PEDIDO_INEXISTENTE` | E2E |
| I: pedido inexistente | id 0 | `GET /api/v1/pedidos/0` | 404, `PEDIDO_INEXISTENTE` | E2E |
| I: ruta inexistente (GET) | — | `GET /api/v1/otra` | 404, `RUTA_INEXISTENTE` | E2E |
| I: ruta inexistente (POST) | — | `POST /api/v1/otra` | 404, `RUTA_INEXISTENTE` | E2E |
| I: sin el id | — | `GET /api/v1/pedidos` | 404, `RUTA_INEXISTENTE` | E2E |
| I: id que no es número | — | `GET /api/v1/pedidos/abc` | 404, `RUTA_INEXISTENTE` | E2E |
| I: `POST` a una ruta de pedido concreto | — | `POST /api/v1/pedidos/1` | 404, `RUTA_INEXISTENTE` | E2E |

### Reglas generales de la API

| Partición | Límites | Caso | Esperado | Nivel |
|-----------|---------|------|----------|-------|
| Formato único de error | cada error | cualquiera de los errores de arriba | el cuerpo es `{"error": {"code": ..., "message": ...}}` con exactamente esas dos claves | E2E |
| Un error nunca devuelve 500 | cuerpos raros | enviar un carrito con ítems de tipos raros (`null`, un número, un texto), talle `null`, cantidad `"3"` | el status nunca es 500 y el formato de error es el único | E2E |
| Flujo completo | creación y consulta | `POST` y luego `GET` del id devuelto | los montos del `GET` coinciden con los del `POST` | E2E |