from dataclasses import dataclass

@dataclass
class Producto:
    id: int
    nombre: str
    precio: float 
    activado: bool