"""El resumen del pedido, desglosado."""

from carrito.descuentos import total_con_descuentos
from carrito.envio import costo_envio
from carrito.impuestos import iva
from carrito.precios import subtotal


def resumen(pedido) -> dict[str, int]:
    """El desglose del pedido, en orden de presentación."""
    base = subtotal(pedido)
    descontado = total_con_descuentos(pedido)
    impuesto = iva(descontado)
    envio = costo_envio(pedido, descontado)

    lineas = {"Subtotal": base}
    if descontado != base:
        lineas["Descuentos"] = descontado - base
    lineas["IVA"] = impuesto
    lineas["Envío"] = envio
    lineas["Total"] = descontado + impuesto + envio
    return lineas
