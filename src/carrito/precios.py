"""Precio de cada línea y subtotal del pedido."""

from carrito.modelo import Linea, Pedido


def precio_linea(linea: Linea) -> int:
    return linea.producto.precio * linea.cantidad


def subtotal(pedido: Pedido) -> int:
    return sum(precio_linea(linea) for linea in pedido.lineas)
