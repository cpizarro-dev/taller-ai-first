"""El resumen del pedido, desglosado."""

from carrito.envio import costo_envio
from carrito.impuestos import iva
from carrito.precios import subtotal


def resumen(pedido):
    """Devuelve las líneas del resumen, en orden de presentación."""
    base = subtotal(pedido)
    impuesto = iva(base)
    envio = costo_envio(pedido, base)
    return [
        ("Subtotal", base),
        ("IVA", impuesto),
        ("Envío", envio),
        ("Total", base + impuesto + envio),
    ]
