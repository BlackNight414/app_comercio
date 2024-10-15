from flask import Blueprint, jsonify
from app.services import RequestCatalogo
import requests

comercio = Blueprint('comercio', __name__)
request_catalogo = RequestCatalogo()

@comercio.route('/catalogo', methods=['GET'])
def catalogo():
    result = requests.get('http://localhost:5001/catalogo/get_all')
    if result.status_code == 200:
        productos = result.json()
        return productos
    else:
        return jsonify('BAD REQUEST')
    
@comercio.route('/catalogo/<int:id>')
def producto(id):
    result = request_catalogo.get_by_id(id)
    if result.status_code == 200:
        producto = result.json()
        return producto
    else:
        return jsonify('BAD REQUEST')