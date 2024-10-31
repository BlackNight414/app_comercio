import requests 
import os

from tenacity import retry, wait_random, stop_after_attempt
from app.services.ms_sin_respuesta import ms_sin_respuesta

class MsPagos:

    __URL_MS = os.getenv('URL_MS_PAGOS')

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3), retry_error_callback=ms_sin_respuesta)
    def registrar_pago(self, producto_id: int, precio: float, medio_pago: str):
        data = {
            'producto_id': producto_id,
            'precio': precio,
            'medio_pago': medio_pago
        }
        resp = requests.post(f'{self.__URL_MS}/registrar_pago', json=data)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception('Microservicio Pagos ha fallado.')
    
    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def eliminar_pago(self, pago_id: int, observaciones: str):
        datos_observaciones = {'observaciones': observaciones}
        resp = requests.delete(f'{self.__URL_MS}/eliminar_pago/{pago_id}', json=datos_observaciones)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception('Microservicio Pagos ha fallado.')