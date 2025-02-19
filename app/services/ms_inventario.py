import requests
import os
import logging

from tenacity import retry, wait_random, stop_after_attempt
from app import cache

class MsInventario:

    __URL_MS = os.getenv('URL_MS_INVENTARIO')

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def ingresar_producto(self, producto_id: int, cantidad: float):
        datos_stock = {
            'producto_id': producto_id,
            'cantidad': cantidad
        }
        resp = requests.post(f'{self.__URL_MS}/ingresar_producto', json=datos_stock, verify=False)
        if resp.status_code == 200:            
            logging.info(f'Se ha ingresado stock al producto id={producto_id}')
            return resp.json()
        else:
            logging.error('Microservicio Inventario ha fallado.')
            raise Exception('Microservicio Inventario ha fallado.')


    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def egresar_producto(self, producto_id: int, cantidad: float):
        datos_stock = {
            'producto_id': producto_id,
            'cantidad': cantidad
        }
        resp = requests.post(f'{self.__URL_MS}/egresar_producto', json=datos_stock, verify=False)
        if resp.status_code in [200, 422]:
            return resp.json()
        else:
            logging.error('Microservicio Inventario ha fallado.')
            raise Exception('Microservicio Inventario ha fallado.')
    
    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def consultar_stock(self, producto_id: int):
        stock = cache.get(f'inventario_stock_producto_id_{producto_id}') # Consultamos el stock en cache
        if stock is None:
            resp = requests.get(f'{self.__URL_MS}/calcular_stock/{producto_id}', verify=False)
            if resp.status_code == 200:
                stock = int(resp.json()['stock'])
            else:
                logging.error('Microservicio Inventario ha fallado.')
                raise Exception('Microservicio Inventario ha fallado.')
        
        logging.info(f'Stock del producto id={producto_id} -> {stock}')
        return stock