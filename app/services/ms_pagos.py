import requests 
import os
import logging

from tenacity import retry, wait_random, stop_after_attempt

class MsPagos:

    __URL_MS = os.getenv('URL_MS_PAGOS')

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def registrar_pago(self, producto_id: int, precio: float, medio_pago: str):
        data = {
            'producto_id': producto_id,
            'precio': precio,
            'medio_pago': medio_pago
        }
        resp = requests.post(f'{self.__URL_MS}/registrar_pago', json=data, verify=False)
        if resp.status_code == 200:
            logging.info('Pago registrado')
            return resp.json()
        else:
            logging.error('Microservicio Pagos ha fallado.')
            raise Exception('Microservicio Pagos ha fallado.')
    
    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def eliminar_pago(self, pago_id: int, observaciones: str):
        datos_observaciones = {'observaciones': observaciones}
        resp = requests.delete(f'{self.__URL_MS}/eliminar_pago/{pago_id}', json=datos_observaciones, verify=False)
        if resp.status_code == 200:
            logging.info(f'Pago id={pago_id} eliminado.')
            return resp.json()
        else:
            logging.error('Microservicio Pagos ha fallado.')
            raise Exception('Microservicio Pagos ha fallado.')