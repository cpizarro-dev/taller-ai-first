"""IVA del pedido."""

IVA = 19


def iva(monto: int) -> int:
    """El IVA que corresponde a `monto`."""
    return int(monto * IVA / 100)


def con_iva(monto: int) -> int:
    return monto + iva(monto)
