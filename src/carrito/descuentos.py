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


def total_con_descuentos(pedido) -> int:
    monto = subtotal(pedido)
    fijos = [c for c in pedido.cupones if c.tipo == "monto"]
    porcentuales = [c for c in pedido.cupones if c.tipo == "porcentaje"]
    for cupon in fijos + porcentuales:
        monto = aplicar_cupon(monto, cupon)
    return monto
