# language: es
#
# Decisiones de negocio (confirmadas, no se discuten):
#   1. El umbral se evalúa ANTES del descuento (sobre el monto bruto del
#      carrito, sin restar cupón ni promoción).
#   2. El IVA CUENTA para el umbral: el monto que se compara con el
#      umbral incluye IVA.
#   3. Las promociones descuentan del monto IGUAL que los cupones: mismo
#      mecanismo, mismo momento de aplicación, solo cambia el origen del
#      descuento (código vs. regla automática).
#   4. Con $50.000 justos el envío ES GRATIS (umbral inclusive, ">=").
#   5. Cliente nuevo: envío gratis siempre, sin importar el monto del
#      carrito (regla ya existente en el código, no se toca).
#
# Nota de modelado: `precio_unitario` es el precio NETO del producto (sin
# IVA), igual que `carrito.modelo.Producto.precio` en el código real. El
# monto que se evalúa contra el umbral es el bruto con IVA, es decir
# `con_iva(subtotal)` (de `carrito.impuestos`), calculado ANTES de restar
# cualquier cupón o promoción, según las decisiones 1 y 2.
#
# El código actual (`carrito/envio.py`, `carrito/resumen.py`) hoy evalúa
# el umbral DESPUÉS del descuento y SIN IVA — lo opuesto a las decisiones
# 1 y 2. Por eso varios escenarios de este archivo van a fallar hasta que
# se actualice el código; solo el de cliente nuevo ya coincide.
#
# Umbral de envío gratis: $50.000.

Característica: Envío gratis del carrito
  Como cliente de la tienda
  Quiero que el envío sea gratis cuando mi carrito alcanza el umbral
  Para no pagar costo de envío en compras suficientemente grandes

  # ---------------------------------------------------------------------
  # Bordes del umbral ($50.000), evaluados sobre el monto bruto CON IVA
  # del carrito (decisiones 1 y 2). No hay cupón ni promoción.
  #
  # monto_evaluado = con_iva(precio_unitario × cantidad)
  #   con_iva(monto) = monto + redondear(monto × 19%)
  #
  #   Control (lejos del borde):  con_iva(16.807) = 16.807 + 3.193 = 20.000
  #   Borde inferior:              con_iva(42.016) = 42.016 + 7.983 = 49.999
  #   Borde exacto:                con_iva(42.017) = 42.017 + 7.983 = 50.000  → decisión 4: gratis
  #   Borde superior:               con_iva(42.018) = 42.018 + 7.983 = 50.001
  # ---------------------------------------------------------------------
  Esquema del escenario: El envío depende de si el carrito alcanza el umbral de $50.000
    Dado un carrito con un producto "<producto>" a $<precio_unitario> con cantidad <cantidad>
    Cuando se calcula el costo de envío del carrito
    Entonces el monto evaluado contra el umbral es $<monto_evaluado>
    Y el envío <resultado>

    Ejemplos:
      | caso                                            | producto             | precio_unitario | cantidad | monto_evaluado | resultado |
      | Caso de control, muy por debajo del umbral      | Mochila urbana       | 16.807           | 1        | 20.000         | se cobra  |
      | Borde inferior: justo por debajo del umbral     | Zapatillas running   | 42.016           | 1        | 49.999         | se cobra  |
      | Borde exacto: el carrito llega justo al umbral  | Campera impermeable  | 42.017           | 1        | 50.000         | es gratis |
      | Borde superior: justo por encima del umbral     | Guantes térmicos     | 42.018           | 1        | 50.001         | es gratis |

  # ---------------------------------------------------------------------
  # Cupón: demuestra la decisión 1 (umbral evaluado ANTES del
  # descuento). El bruto con IVA ya alcanza el umbral, así que el envío
  # sigue siendo gratis aunque el cupón haga bajar mucho lo que el
  # cliente termina pagando.
  #
  # Subtotal neto:                 45.000 × 1 = 45.000
  # Monto evaluado (con IVA, antes del descuento): con_iva(45.000) = 45.000 + 8.550 = 53.550  (≥ 50.000 → gratis)
  # Descuento cupón (20%):          porcentaje(45.000, 20) = 9.000
  # Neto tras descuento:            45.000 − 9.000 = 36.000
  # Monto que paga el cliente (con IVA): 36.000 + iva(36.000) = 36.000 + 6.840 = 42.840
  # ---------------------------------------------------------------------
  Escenario: El cupón no quita el envío gratis aunque el monto a pagar quede bajo el umbral
    Dado un carrito con un producto "Campera de cuero" a $45.000 con cantidad 1
    Y un cupón "DESCUENTO20" que aplica un 20% de descuento sobre el carrito
    Cuando se calcula el costo de envío del carrito
    Entonces el monto evaluado contra el umbral es $53.550
    Y el descuento aplicado es $9.000
    Y el monto que paga el cliente es $42.840
    Y el envío es gratis

  # ---------------------------------------------------------------------
  # Promoción: demuestra la decisión 3 (las promociones descuentan igual
  # que los cupones, incluido el momento de evaluación del umbral).
  # Mismo mecanismo que el escenario del cupón.
  #
  # Subtotal neto:                 43.000 × 1 = 43.000
  # Monto evaluado (con IVA, antes del descuento): con_iva(43.000) = 43.000 + 8.170 = 51.170  (≥ 50.000 → gratis)
  # Descuento promoción (20%):      porcentaje(43.000, 20) = 8.600
  # Neto tras descuento:            43.000 − 8.600 = 34.400
  # Monto que paga el cliente (con IVA): 34.400 + iva(34.400) = 34.400 + 6.536 = 40.936
  # ---------------------------------------------------------------------
  Escenario: La promoción no quita el envío gratis, igual que un cupón
    Dado un carrito con un producto "Campera softshell" a $43.000 con cantidad 1
    Y una promoción "20% de descuento de temporada" que aplica un 20% de descuento sobre el carrito
    Cuando se calcula el costo de envío del carrito
    Entonces el monto evaluado contra el umbral es $51.170
    Y el descuento aplicado es $8.600
    Y el monto que paga el cliente es $40.936
    Y el envío es gratis

  # ---------------------------------------------------------------------
  # Cliente nuevo: un cliente sin compras previas tiene envío gratis
  # siempre, sin importar el monto del carrito. Esta excepción se aplica
  # antes que el umbral y lo deja sin efecto (alineado con
  # `free_shipping_for_new_customer` en src/carrito/envio.py).
  #
  # Subtotal neto: 15.000 × 1 = 15.000
  # Monto evaluado (con IVA), solo a modo informativo ya que la
  # excepción de cliente nuevo ni siquiera llega a mirarlo:
  #   con_iva(15.000) = 15.000 + 2.850 = 17.850  (< 50.000, y aun así gratis)
  # ---------------------------------------------------------------------
  Escenario: Un cliente nuevo tiene envío gratis aunque el carrito no llegue al umbral
    Dado un cliente nuevo sin compras previas
    Y un carrito con un producto "Cargador USB-C" a $15.000 con cantidad 1
    Cuando se calcula el costo de envío del carrito
    Entonces el monto evaluado contra el umbral es $17.850
    Y el envío es gratis
