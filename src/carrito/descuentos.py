"""Descuentos del pedido."""

from carrito.dinero import porcentaje
from carrito.modelo import Cupon
from carrito.precios import subtotal


def aplicar_cupon(monto: int, cupon: Cupon) -> int:
    return monto - porcentaje(monto, cupon.valor)


def total_con_descuentos(pedido) -> int:
    monto = subtotal(pedido)
    for cupon in pedido.cupones:
        monto = aplicar_cupon(monto, cupon)
    return monto
