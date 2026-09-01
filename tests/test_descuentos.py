"""Verifica el orden documentado de los cupones: primero el porcentual,
después el de monto fijo (ver README.md y el docstring de carrito.descuentos).
"""

from carrito.descuentos import total_con_descuentos
from carrito.modelo import Cupon, Linea, Pedido, Producto


def test_cupon_porcentual_se_aplica_antes_que_el_de_monto_fijo():
    producto = Producto(sku="SKU-1", nombre="Producto de prueba", precio=10_000)
    linea = Linea(producto=producto, cantidad=1)
    cupon_monto = Cupon(codigo="VALE2000", tipo="monto", valor=2_000)
    cupon_porcentaje = Cupon(codigo="DESC10", tipo="porcentaje", valor=10)

    pedido = Pedido(
        numero=1,
        lineas=[linea],
        cupones=[cupon_monto, cupon_porcentaje],
    )

    # Subtotal: 10.000
    # 1) Cupón porcentual (10%) primero: 10.000 - 1.000 = 9.000
    # 2) Cupón de monto fijo después: 9.000 - 2.000 = 7.000
    assert total_con_descuentos(pedido) == 7_000
