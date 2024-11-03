from dataclasses import dataclass, InitVar

@dataclass
class Carrito:
    producto_id: int
    cantidad: float
    medio_pago: str
    direccion_envio: str

    compra_id: int = None
    pago_id: int = None
    precio_pago: float = None