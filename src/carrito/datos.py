"""Lectura de los pedidos de ejemplo."""

import json
from pathlib import Path

from carrito.modelo import Linea, Pedido, Producto

ARCHIVO = Path(__file__).resolve().parents[2] / "datos" / "ejemplo.json"


def cargar():
    contenido = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    productos = {p["sku"]: Producto(**p) for p in contenido["productos"]}
    pedidos = {}
    for crudo in contenido["pedidos"]:
        lineas = [Linea(productos[l["sku"]], l["cantidad"]) for l in crudo["lineas"]]
        pedidos[crudo["numero"]] = Pedido(numero=crudo["numero"], lineas=lineas)
    return pedidos


def pedido(numero: int) -> Pedido:
    return cargar()[numero]
