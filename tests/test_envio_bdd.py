"""Steps de pytest-bdd para tests/features/envio.feature.

Las decisiones 1 y 2 (umbral evaluado ANTES del descuento, y CON IVA)
todavía no están implementadas en `carrito.envio` / `carrito.resumen`:
hoy el umbral se evalúa sobre el monto ya descontado y sin IVA. Por eso
varios escenarios de este archivo fallan a propósito — son la
especificación objetivo, no una descripción del comportamiento actual.
Solo el escenario de cliente nuevo ya coincide con el código real.

No se modifica nada en `src/carrito`: los steps solo llaman a las
funciones reales (`subtotal`, `con_iva`, `iva`, `aplicar_cupon`,
`total_con_descuentos`, `costo_envio`) y verifican los montos contra
ellas.
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from carrito.descuentos import aplicar_cupon, total_con_descuentos
from carrito.dinero import porcentaje
from carrito.envio import costo_envio
from carrito.impuestos import con_iva, iva
from carrito.modelo import Cupon, Linea, Pedido, Producto
from carrito.precios import subtotal

scenarios("features/envio.feature")


def _pesos(texto: str) -> int:
    """Convierte un monto en formato '50.000' al entero 50000."""
    return int(texto.replace(".", ""))


@pytest.fixture
def pedido():
    return Pedido(numero=1)


@pytest.fixture
def promocion_pendiente():
    """`descuentos.PROMOCIONES` no tiene una promoción porcentual genérica
    todavía, así que la promoción de estos escenarios no se puede rutear
    por `pedido.promociones`. Se guarda acá y el step "Cuando" la aplica
    a mano con `dinero.porcentaje`, el mismo cálculo que usa un cupón.
    """
    return {}


@pytest.fixture
def resultado():
    return {}


@given("un cliente nuevo sin compras previas")
def cliente_nuevo(pedido):
    pedido.cliente_nuevo = True


@given(
    parsers.parse(
        'un carrito con un producto "{nombre}" a ${precio} con cantidad {cantidad:d}'
    )
)
def carrito_con_un_producto(pedido, nombre, precio, cantidad):
    producto = Producto(sku=nombre, nombre=nombre, precio=_pesos(precio))
    pedido.lineas.append(Linea(producto=producto, cantidad=cantidad))


@given(
    parsers.parse(
        'un cupón "{codigo}" que aplica un {porcentaje:d}% de descuento sobre el carrito'
    )
)
def cupon(pedido, codigo, porcentaje):
    pedido.cupones.append(Cupon(codigo=codigo, tipo="porcentaje", valor=porcentaje))


@given(
    parsers.parse(
        'una promoción "{nombre}" que aplica un {porcentaje:d}% de descuento sobre el carrito'
    )
)
def promocion(promocion_pendiente, nombre, porcentaje):
    promocion_pendiente["nombre"] = nombre
    promocion_pendiente["porcentaje"] = porcentaje


@when("se calcula el costo de envío del carrito")
def calcular_envio(pedido, promocion_pendiente, resultado):
    bruto = subtotal(pedido)
    # Decisiones 1 y 2: el monto contra el umbral es el bruto CON IVA,
    # ANTES de restar cupón o promoción.
    resultado["monto_evaluado"] = con_iva(bruto)

    if promocion_pendiente:
        descuento = porcentaje(bruto, promocion_pendiente["porcentaje"])
        neto_descontado = bruto - descuento
        resultado["descuento"] = descuento
    else:
        neto_descontado = total_con_descuentos(pedido)
        if neto_descontado != bruto:
            resultado["descuento"] = bruto - neto_descontado

    resultado["monto_pagado"] = neto_descontado + iva(neto_descontado)

    # Comportamiento real de HOY (sin tocar carrito.envio): usa el monto
    # ya descontado, sin IVA — lo que hace resumen.py en producción.
    resultado["envio"] = costo_envio(pedido, neto_descontado)


@then(parsers.parse("el monto evaluado contra el umbral es ${monto}"))
def verificar_monto_evaluado(resultado, monto):
    assert resultado["monto_evaluado"] == _pesos(monto)


@then(parsers.parse("el descuento aplicado es ${monto}"))
def verificar_descuento(resultado, monto):
    assert resultado["descuento"] == _pesos(monto)


@then(parsers.parse("el monto que paga el cliente es ${monto}"))
def verificar_monto_pagado(resultado, monto):
    assert resultado["monto_pagado"] == _pesos(monto)


@then("el envío es gratis")
def verificar_envio_gratis(resultado):
    assert resultado["envio"] == 0


@then("el envío se cobra")
def verificar_envio_se_cobra(resultado):
    assert resultado["envio"] > 0
