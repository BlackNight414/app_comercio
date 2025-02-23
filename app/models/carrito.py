from dataclasses import dataclass
from app.models.producto import Producto

@dataclass
class Carrito:
    producto_id: int
    cantidad: float
    medio_pago: str
    direccion_envio: str

    producto: Producto = None
    compra_id: int = None
    pago_id: int = None
    stock_id: int = None
    precio_pago: float = None