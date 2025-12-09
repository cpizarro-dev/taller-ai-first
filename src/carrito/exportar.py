"""Exporta el resumen de un pedido a CSV."""

import csv


def a_csv(resumen, salida):
    """Escribe el resumen en `salida`, una fila por línea del desglose."""
    escritor = csv.writer(salida)
    escritor.writerow(["concepto", "monto"])
    for etiqueta, monto in resumen:
        escritor.writerow([etiqueta, monto])
