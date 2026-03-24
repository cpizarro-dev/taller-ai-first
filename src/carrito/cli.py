"""Línea de comandos del carrito."""

import argparse

from carrito.datos import pedido
from carrito.descuentos import PROMOCIONES
from carrito.resumen import resumen


def main():
    parser = argparse.ArgumentParser(prog="carrito")
    parser.add_argument("comando", choices=["total"])
    parser.add_argument("--pedido", type=int, required=True)
    parser.add_argument("--sin", action="append", choices=sorted(PROMOCIONES), default=[])
    args = parser.parse_args()

    elegido = pedido(args.pedido)
    elegido.promociones = [p for p in elegido.promociones if p not in args.sin]
    for etiqueta, monto in resumen(elegido).items():
        print(etiqueta, monto)


if __name__ == "__main__":
    main()
