"""El resumen del pedido, desglosado."""

from carrito.impuestos import iva
from carrito.precios import subtotal


def resumen(pedido):
    """Devuelve las líneas del resumen, en orden de presentación."""
    base = subtotal(pedido)
    impuesto = iva(base)
    return [
        ("Subtotal", base),
        ("IVA", impuesto),
        ("Total", base + impuesto),
    ]
