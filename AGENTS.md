# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos

```sh
uv sync                                    # instalar dependencias (incl. dev)
uv run pytest                              # correr toda la suite
uv run pytest -v                           # con detalle por test
uv run pytest tests/test_descuentos.py -k test_cupon_porcentual_se_aplica_antes_que_el_de_monto_fijo
                                            # correr un test puntual
uv run python -m carrito total --pedido 42 # correr el CLI (numero de pedido de datos/ejemplo.json)
uv run python -m carrito total --pedido 42 --detalle       # con desglose línea por línea
uv run python -m carrito total --pedido 46 --sin primera-compra  # desactivar una promoción
```

No hay linter ni formateador configurado en `pyproject.toml`; la única dependencia de dev es `pytest`. CI (`.github/workflows/tests.yml`) corre `uv sync --locked && uv run pytest` en cada push/PR.

## Convenciones

El código actual mezcla nombres en español (`promo_2x1`, `costo_envio`, parámetros `pedido`/`monto`) con algunos en inglés (`volume_discount(order, amount)` en `descuentos.py`, `free_shipping_for_new_customer(order)` en `envio.py`). **De ahora en adelante, todo código nuevo se escribe en inglés** (nombres de funciones, parámetros, variables). No hace falta traducir lo existente de forma proactiva, pero si tocás una función que está en español, aprovechá para migrarla a inglés en el mismo cambio.

## Regla arbitral: documentación vs. código

Cuando la documentación (README, docstrings) contradiga lo que el código realmente hace, **la documentación manda** — asumí que describe el comportamiento correcto y el código tiene el bug. Pero antes de aplicar ese criterio, **avisame explícitamente de la contradicción** (qué dice la doc, qué hace el código, dónde) para que yo confirme antes de que ajustes el código.

## Arquitectura

Paquete `src/carrito`, instalable en modo editable vía hatchling. El flujo va de `cli.py` → `datos.py` (carga) → una cadena de módulos de cálculo puros → `resumen.py` (agrega el desglose para mostrar).

**Origen de datos**: `datos.py` lee `datos/ejemplo.json` completo en cada llamada a `cargar()` (no hay caché ni base de datos — es el catálogo + pedidos de ejemplo). `pedido(numero)` arma un `Pedido` (ver `modelo.py`) o lanza `KeyError` si el número no existe.

**Orden de cálculo del total** (la parte no obvia, repartida en varios archivos — ver `descuentos.py`, `impuestos.py`, `envio.py`, `resumen.py`):

1. `subtotal()` — suma de `precio_linea` por cada línea.
2. `descuento_promociones()` (en `descuentos.py`) — resta las promociones activas en `pedido.promociones` (`PROMOCIONES` = `2x1`, `volumen`, `primera-compra`; controlables desde el CLI con `--sin`). **Esto se aplica antes que los cupones**, aunque ni el README ni el docstring del módulo lo mencionan explícitamente.
3. Cupones de `pedido.cupones`: primero los `tipo="porcentaje"`, después los `tipo="monto"` — el orden importa y está cubierto por `tests/test_descuentos.py`.
4. `iva()` sobre el monto ya descontado (19%, constante `IVA` en `impuestos.py`).
5. `costo_envio()`: si `pedido.cliente_nuevo` es `True`, envío gratis sin importar región ni monto (chequeo que ocurre *antes* que el umbral por monto); si no, gratis sobre `UMBRAL_ENVIO_GRATIS` (50.000) o según el tramo de `TRAMOS` por región (`envio.py`).

**Dinero**: todo se maneja en pesos enteros. `dinero.py` centraliza el redondeo (`redondear`, `porcentaje`) y su docstring establece que todo cálculo porcentual debe redondear al peso más cercano — pero `impuestos.iva()` no usa esas utilidades y trunca con `int(...)` en vez de redondear. Tenerlo en cuenta antes de asumir que todo el módulo de impuestos sigue la misma convención que `descuentos.py` (que sí usa `dinero.porcentaje`).

**Modelos** (`modelo.py`): `Producto`, `Cupon` son dataclasses `frozen`; `Linea` y `Pedido` son mutables. `Pedido.promociones` es una lista de claves de `PROMOCIONES`, no objetos.

**CLI** (`cli.py`): un solo subcomando (`total`), argumentos `--pedido` (obligatorio), `--sin` (repetible, filtra promociones antes de calcular), `--detalle` (imprime línea por línea antes del resumen). El resumen (`resumen.py`) devuelve un `dict` ordenado por inserción que el CLI imprime alineando columnas por ancho máximo.
