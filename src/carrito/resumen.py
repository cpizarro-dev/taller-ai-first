"""El resumen del pedido, desglosado."""

from carrito.descuentos import total_con_descuentos
from carrito.envio import costo_envio
from carrito.impuestos import iva
from carrito.precios import subtotal


def resumen(pedido):
    """Devuelve las líneas del resumen, en orden de presentación."""
    base = subtotal(pedido)
    descontado = total_con_descuentos(pedido)
    impuesto = iva(descontado)
    envio = costo_envio(pedido, descontado)
    lineas = [("Subtotal", base)]
    if descontado != base:
        lineas.append(("Descuentos", descontado - base))
    lineas.append(("IVA", impuesto))
    lineas.append(("Envío", envio))
    lineas.append(("Total", descontado + impuesto + envio))
    return lineas
