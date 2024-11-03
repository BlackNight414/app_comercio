import requests
import os

from tenacity import retry, wait_random, stop_after_attempt

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
            return resp
        else:
            raise Exception('Microservicio Inventario ha fallado.')
    
    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def consultar_stock(self, producto_id: int):
        resp = requests.get(f'{self.__URL_MS}/calcular_stock/{producto_id}')
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception('Microservicio Inventario ha fallado.')