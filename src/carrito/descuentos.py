"""Descuentos del pedido.

La política comercial fija el orden en que se aplican: primero los descuentos
porcentuales, y sobre el monto que queda, los vales de monto fijo. El orden
solo se nota cuando el pedido trae más de un descuento, pero cambia el total.
"""

from carrito.dinero import porcentaje
from carrito.modelo import Cupon
from carrito.precios import subtotal


def aplicar_cupon(monto: int, cupon: Cupon) -> int:
    if cupon.tipo == "porcentaje":
        return monto - porcentaje(monto, cupon.valor)
    if cupon.tipo == "monto":
        return max(0, monto - cupon.valor)
    raise ValueError(f"Tipo de cupón desconocido: {cupon.tipo}")


def promo_2x1(pedido, monto: int) -> int:
    """Por cada par de unidades de una misma línea, una sale gratis."""
    return sum(
        (linea.cantidad // 2) * linea.producto.precio for linea in pedido.lineas
    )


PROMOCIONES = {
    "2x1": promo_2x1,
}


def descuento_promociones(pedido, monto: int) -> int:
    return sum(PROMOCIONES[nombre](pedido, monto) for nombre in pedido.promociones)


def total_con_descuentos(pedido) -> int:
    monto = subtotal(pedido)
    monto -= descuento_promociones(pedido, monto)
    fijos = [c for c in pedido.cupones if c.tipo == "monto"]
    porcentuales = [c for c in pedido.cupones if c.tipo == "porcentaje"]
    for cupon in fijos + porcentuales:
        monto = aplicar_cupon(monto, cupon)
    return max(0, monto)
