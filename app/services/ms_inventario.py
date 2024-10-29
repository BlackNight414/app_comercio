import requests
import os
from datetime import date

from tenacity import retry, wait_random, stop_after_attempt
from app.services.ms_sin_respuesta import ms_sin_respuesta

class MsInventario:

    __URL_MS = os.getenv('URL_MS_INVENTARIO')

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3), retry_error_callback=ms_sin_respuesta)
    def egresar_producto(self, producto_id: int, cantidad: float):
        datos_stock = {
            'producto_id': producto_id,
            'cantidad': cantidad
        }
        resp = requests.post(f'{self.__URL_MS}/egresar_producto', json=datos_stock)
        return resp
    
    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3), retry_error_callback=ms_sin_respuesta)
    def consultar_stock(self, producto_id: int):
        resp = requests.get(f'{self.__URL_MS}/calcular_stock/{producto_id}')
        return resp