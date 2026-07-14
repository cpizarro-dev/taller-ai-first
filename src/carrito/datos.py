"""Lectura de los pedidos de ejemplo."""

import json
from pathlib import Path

from carrito.modelo import Cupon, Linea, Pedido, Producto

ARCHIVO = Path(__file__).resolve().parents[2] / "datos" / "ejemplo.json"


def cargar():
    contenido = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    productos = {p["sku"]: Producto(**p) for p in contenido["productos"]}
    pedidos = {}
    for crudo in contenido["pedidos"]:
        lineas = [Linea(productos[l["sku"]], l["cantidad"]) for l in crudo["lineas"]]
        pedidos[crudo["numero"]] = Pedido(
            numero=crudo["numero"],
            lineas=lineas,
            region=crudo.get("region", "metropolitana"),
            cupones=[Cupon(**c) for c in crudo.get("cupones", [])],
            promociones=crudo.get("promociones", []),
            cliente_nuevo=crudo.get("cliente_nuevo", False),
        )
    return pedidos


def pedido(numero: int) -> Pedido:
    """El pedido con ese número. Lanza KeyError si no existe."""
    return cargar()[numero]
