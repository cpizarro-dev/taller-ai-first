"""Línea de comandos del carrito."""

import argparse
import sys

from carrito.datos import pedido
from carrito.exportar import a_csv
from carrito.resumen import resumen


def main():
    parser = argparse.ArgumentParser(prog="carrito")
    parser.add_argument("comando", choices=["total"])
    parser.add_argument("--pedido", type=int, required=True)
    parser.add_argument("--csv", action="store_true")
    args = parser.parse_args()

    lineas = resumen(pedido(args.pedido))
    if args.csv:
        a_csv(lineas, sys.stdout)
        return
    for etiqueta, monto in lineas:
        print(etiqueta, monto)


if __name__ == "__main__":
    main()
