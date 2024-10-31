from flask import Blueprint, jsonify, request
from app.services import OrquestadorManual, OrquestadorSaga

from app.services import MsCatalogo
from app.mapping import CarritoSchema
from app.models import Carrito

comercio = Blueprint('comercio', __name__)
carrito_schema = CarritoSchema()

@comercio.route('/comprar_producto_manual', methods=['POST'])
def comprar_producto():
    
    datos_compra = request.get_json()

    producto_id = datos_compra['producto_id']
    cantidad = datos_compra['cantidad']
    medio_pago = datos_compra['medio_pago']
    direccion = datos_compra['direccion']

    orquestador_compra = OrquestadorManual()
    try:
        resp = orquestador_compra.comprar_producto(producto_id, cantidad, medio_pago, direccion)
        return jsonify(resp)
    except BaseException as e:
        print(e)
        return jsonify('Proceso Orquestador ha fallado.')

@comercio.route('/comprar_producto_saga', methods=['POST']) 
def comprar_producto_saga():    
    datos_compra = request.get_json()

    producto_id = datos_compra['producto_id']
    cantidad = datos_compra['cantidad']
    medio_pago = datos_compra['medio_pago']
    direccion = datos_compra['direccion']

    orquestador_compra = OrquestadorSaga()
    
    exito = orquestador_compra.proceso_compra(producto_id, cantidad, medio_pago, direccion)

    if exito:
        resp = jsonify('¡PROCESO DE COMPRA COMPLETADO CON EXITO! :D')
    else:
        resp = jsonify('PROCESO DE COMPRA HA FALLADO :(')
    return resp, 200
    
@comercio.route('/catalogo/<int:id>')
def producto(id):
    ms_catalogo = MsCatalogo()
    result = ms_catalogo.get_by_id(id)

    if result.status_code == 200:
        producto = result.json()
        return producto
    else:
        return jsonify('Microservicio Catalogo no responde')
    
