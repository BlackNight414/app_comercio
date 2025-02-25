import requests
import os
from tenacity import retry, stop_after_attempt , wait_random

from app.models import Producto
from app.mapping import ProductoSchema
from app import cache

import logging

producto_schema = ProductoSchema()

class MsCatalogo:

    __URL_MS = os.getenv('URL_MS_CATALOGO') # Busca la URL en variables de entorno

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def get_by_id(self, id: int) -> Producto:
        producto = cache.get(f'producto_id_{id}')
        if producto is None:
            resp = requests.get(url=f'{self.__URL_MS}/get_by_id/{id}', verify=False)
            if resp.status_code == 200:
                if 'NOT FOUND' in resp.json().values(): # Lanzamos excepción si no existe el producto
                    raise Exception(f'Producto id={id} no existe.')

                producto = producto_schema.load(resp.json())
                cache.set(f'producto_id_{id}', producto, timeout=30)
            else:
                logging.error('Microservicio Catálogo ha fallado.')
                raise Exception('Microservicio Catálogo ha fallado.')
        
        logging.info(f'Se ha consultado el producto id={producto.id}')
        return producto
    