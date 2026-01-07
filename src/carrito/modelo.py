"""Los objetos del pedido."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Producto:
    sku: str
    nombre: str
    precio: int


@dataclass
class Linea:
    producto: Producto
    cantidad: int


@dataclass(frozen=True)
class Cupon:
    codigo: str
    valor: int


@dataclass
class Pedido:
    numero: int
    lineas: list[Linea] = field(default_factory=list)
    region: str = "metropolitana"
    cupones: list[Cupon] = field(default_factory=list)
