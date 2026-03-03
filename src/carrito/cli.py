"""Línea de comandos del carrito."""

import argparse

from carrito.datos import pedido
from carrito.resumen import resumen


def main():
    parser = argparse.ArgumentParser(prog="carrito")
    parser.add_argument("comando", choices=["total"])
    parser.add_argument("--pedido", type=int, required=True)
    args = parser.parse_args()

    for etiqueta, monto in resumen(pedido(args.pedido)):
        print(etiqueta, monto)


if __name__ == "__main__":
    main()
