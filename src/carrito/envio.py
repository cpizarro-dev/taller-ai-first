"""Costo de envío según la región de destino.

Sobre cierto monto el envío no se cobra. El umbral se compara contra el monto
que el cliente efectivamente paga por los productos.
"""

TRAMOS = {
    "metropolitana": 3990,
    "regiones": 5990,
    "extremo": 9990,
}

UMBRAL_ENVIO_GRATIS = 50000


def costo_envio(pedido, monto: int) -> int:
    if monto >= UMBRAL_ENVIO_GRATIS:
        return 0
    return TRAMOS.get(pedido.region, TRAMOS["regiones"])
