import requests
import os

from tenacity import retry, wait_random, stop_after_attempt
from app import cache

class MsInventario:

    __URL_MS = os.getenv('URL_MS_INVENTARIO')

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def egresar_producto(self, producto_id: int, cantidad: float):
        datos_stock = {
            'producto_id': producto_id,
            'cantidad': cantidad
        }
        resp = requests.post(f'{self.__URL_MS}/egresar_producto', json=datos_stock)
        if resp.status_code == 200:

            # Actualizamos el stock de cache si es que existe
            stock = cache.get(f'stock_producto_id_{producto_id}')
            if stock:
                cache.set(f'stock_producto_id_{producto_id}', stock-cantidad, timeout=60)
            
            return resp
        else:
            raise Exception('Microservicio Inventario ha fallado.')
    
    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def consultar_stock(self, producto_id: int):
        stock = cache.get(f'stock_producto_id_{producto_id}') # Consultamos el stock en cache
        if stock is None:
            resp = requests.get(f'{self.__URL_MS}/calcular_stock/{producto_id}')
            if resp.status_code == 200:
                stock = float(resp.json()['stock'])
                cache.set(f'stock_producto_id_{producto_id}', stock, timeout=60) # Guardamos el stock en cache
            else:
                raise Exception('Microservicio Inventario ha fallado.')
        
        return stock