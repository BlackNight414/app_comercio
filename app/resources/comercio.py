from flask import Blueprint, jsonify, request
from app.services import OrquestadorManual, OrquestadorSaga
import logging
from app.services import MsCatalogo
from app.mapping import CarritoSchema, ProductoSchema
from app.models import Carrito

comercio = Blueprint('comercio', __name__)
carrito_schema = CarritoSchema()
producto_schema= ProductoSchema()

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
        logging.error(e)
        return jsonify('Proceso Orquestador ha fallado.')

@comercio.route('/comprar_producto_saga', methods=['POST']) 
def comprar_producto_saga():    
    datos_compra = request.get_json()
    carrito = carrito_schema.load(datos_compra)

    orquestador_compra = OrquestadorSaga()
    
    exito = orquestador_compra.proceso_compra(carrito)

    if exito:
        logging.info('Proceso de compra de producto completado.')
        resp = carrito_schema.dump(carrito)
    else:
        logging.error('El proceso de compra no pudo completarse.')
        resp = jsonify('PROCESO DE COMPRA HA FALLADO :(')
    return resp, 200
    
@comercio.route('/catalogo/<int:id>')
def producto(id):
    ms_catalogo = MsCatalogo()

    try:
        producto = ms_catalogo.get_by_id(id)
        return producto_schema.dump(producto), 200
    except Exception as e:
        logging.error(e)
        return jsonify('Microservicio Catalogo no responde.'), 500    
