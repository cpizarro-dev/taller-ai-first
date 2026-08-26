"""Línea de comandos del carrito."""

import argparse

from carrito.datos import pedido
from carrito.descuentos import PROMOCIONES
from carrito.precios import precio_linea
from carrito.resumen import resumen


def main():
    parser = argparse.ArgumentParser(prog="carrito")
    parser.add_argument("comando", choices=["total"])
    parser.add_argument("--pedido", type=int, required=True)
    parser.add_argument("--sin", action="append", choices=sorted(PROMOCIONES), default=[])
    parser.add_argument("--detalle", action="store_true")
    args = parser.parse_args()

    elegido = pedido(args.pedido)
    elegido.promociones = [p for p in elegido.promociones if p not in args.sin]
    filas = resumen(elegido)
    ancho_monto = max(len(str(monto)) for monto in filas.values())

    if args.detalle:
        precios_linea = [precio_linea(linea) for linea in elegido.lineas]
        ancho_monto = max(ancho_monto, *(len(str(p)) for p in precios_linea))
        ancho_nombre = max(len(linea.producto.nombre) for linea in elegido.lineas)
        for linea, precio in zip(elegido.lineas, precios_linea):
            nombre = f"{linea.producto.nombre:<{ancho_nombre}}"
            print(f"{nombre} x {linea.cantidad} {precio:>{ancho_monto}}")
        print("-")

    ancho_etiqueta = max(len(etiqueta) for etiqueta in filas)
    for etiqueta, monto in filas.items():
        print(f"{etiqueta:<{ancho_etiqueta}} {monto:>{ancho_monto}}")


if __name__ == "__main__":
    main()
