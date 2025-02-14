import requests
import os
import logging
from tenacity import retry, stop_after_attempt, wait_random

class MsCompras:

    __URL_MS = os.getenv('URL_MS_COMPRAS') # Busca la URL en variables de entorno

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def registrar_compra(self, producto_id: int, direccion: str):
        data = {
            'producto_id': producto_id,
            'direccion_envio': direccion}
        resp = requests.post(f'{self.__URL_MS}/registrar_compra', json=data, verify=False)
        if resp.status_code == 200:
            logging.info(f'Compra registrada')
            return resp.json()
        else:
            logging.error('Microservicio Compras ha fallado.')
            raise Exception('Microservicio Compras ha fallado.')
        
    def eliminar_compra(self, id_compra: int, observaciones: str):
        datos_observaciones = {'observaciones': observaciones}
        resp = requests.delete(f'{self.__URL_MS}/eliminar_compra/{id_compra}', json=datos_observaciones, verify=False)
        if resp.status_code == 200:
            logging.info(f'Compra id={id_compra} eliminada')
            return resp.json()
        else:
            raise Exception('Microservicio Compras ha fallado.')
    
    

    