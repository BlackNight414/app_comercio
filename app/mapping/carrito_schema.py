from marshmallow import Schema, fields, post_load
from app.models import Carrito

class CarritoSchema(Schema):
    producto_id: int = fields.Integer(required=True)
    cantidad: float = fields.Float(required=True)
    medio_pago: str = fields.String(required=True)
    direccion_envio: str = fields.String(required=True)

    # Datos relacionados del carrito. Solamente a modo lectura
    compra_id: int = fields.Integer(dump_only=True)
    pago_id: int = fields.Integer(dump_only=True)
    precio_pago: float = fields.Float(dump_only=True)

    @post_load
    def deserealizar_carrito(self, data, **kwargs):
        return Carrito(**data)
