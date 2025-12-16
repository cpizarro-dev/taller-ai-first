"""Costo de envío según la región de destino."""

TRAMOS = {
    "metropolitana": 3990,
    "regiones": 5990,
    "extremo": 9990,
}


def costo_envio(pedido) -> int:
    return TRAMOS.get(pedido.region, TRAMOS["regiones"])
