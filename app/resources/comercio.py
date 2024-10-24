from flask import Blueprint, jsonify, request
from app.services import OrquestadorManual, OrquestadorSaga
import requests
from saga import SagaBuilder
from datetime import date

from app.services import MsCatalogo

comercio = Blueprint('comercio', __name__)

@comercio.route('/comprar_producto_manual', methods=['POST'])
def comprar_producto():
    
    datos_compra = request.get_json()

    print(datos_compra)
    producto_id = datos_compra['producto_id']
    cantidad = datos_compra['cantidad']
    fecha_compra = date.fromisoformat(datos_compra['fecha_compra']) # Convierto a tipo date desde formato de fecha iso (comunmente en los formularios)
    medio_pago = datos_compra['medio_pago']
    direccion = datos_compra['direccion']

    orquestador_compra = OrquestadorManual()
    try:
        resp = orquestador_compra.comprar_producto(producto_id, cantidad, fecha_compra, medio_pago, direccion)
        return jsonify(resp)
    except BaseException as e:
        print(e)
        return jsonify('Proceso Orquestador ha fallado.')

@comercio.route('/comprar_producto_saga', methods=['POST']) 
def comprar_producto_saga():

    datos_compra = request.get_json()

    producto_id = datos_compra['producto_id']
    cantidad = datos_compra['cantidad']
    fecha_compra = date.fromisoformat(datos_compra['fecha_compra']) # Convierto a tipo date desde formato de fecha iso (comunmente en los formularios)
    medio_pago = datos_compra['medio_pago']
    direccion = datos_compra['direccion']

    orquestador_compra = OrquestadorSaga()
    
    exito = orquestador_compra.proceso_compra(producto_id, cantidad, fecha_compra, medio_pago, direccion)

    if exito:
        resp = jsonify('¡PROCESO DE COMPRA COMPLETADO CON EXITO! :D')
    else:
        resp = jsonify('PROCESO DE COMPRA HA FALLADO :(')
    return resp, 200


@comercio.route('/catalogo', methods=['GET'])
def catalogo():
    result = requests.get('http://localhost:5001/catalogo/get_all')
    if result.status_code == 200:
        productos = result.json()
        return productos
    else:
        return jsonify('ERROR')
    
@comercio.route('/catalogo/<int:id>')
def producto(id):
    ms_catalogo = MsCatalogo()
    result = ms_catalogo.get_by_id(id)

    if result.status_code == 200:
        producto = result.json()
        return producto
    else:
        return jsonify('Microservicio Catalogo no responde')
    
