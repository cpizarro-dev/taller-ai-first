"""Aritmética de pesos.

Todo se guarda en pesos enteros: el sistema no maneja fracciones. Cuando un
cálculo produce decimales —un porcentaje, un prorrateo— se redondea al peso
más cercano antes de seguir.
"""


def redondear(valor: float) -> int:
    """Redondea al peso más cercano. El medio peso va hacia arriba."""
    if valor >= 0:
        return int(valor + 0.5)
    return -int(-valor + 0.5)


def porcentaje(monto: int, tasa: int) -> int:
    """El `tasa`% de `monto`, redondeado al peso."""
    return redondear(monto * tasa / 100)
