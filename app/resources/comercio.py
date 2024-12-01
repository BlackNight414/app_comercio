from flask import Blueprint, jsonify, request
from app.services import OrquestadorManual, OrquestadorSaga
import logging
from app.services import MsCatalogo, MsInventario
from app.mapping import CarritoSchema, ProductoSchema
from app.models import Carrito

comercio = Blueprint('comercio', __name__)
carrito_schema = CarritoSchema()
producto_schema= ProductoSchema()

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
        return jsonify('Microservicio Catalogo no responde.'), 200

@comercio.route('/consultar_stock/<int:producto_id>')
def consultar_stock(producto_id):
    ms_inventario = MsInventario()
    try:
        stock = ms_inventario.consultar_stock(producto_id)
        return jsonify({'stock': stock}), 200
    except Exception as e:
        logging.error(e)
        return jsonify('Microservicio Inventario no responde'), 200
    
