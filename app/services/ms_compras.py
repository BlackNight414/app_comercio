import requests
import os
from datetime import date
from tenacity import retry, stop_after_attempt, wait_random

from app.services.ms_sin_respuesta import ms_sin_respuesta


class MsCompras:

    __URL_MS = os.getenv('URL_MS_COMPRAS') # Busca la URL en variables de entorno

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3), retry_error_callback=ms_sin_respuesta)
    def registrar_compra(self, producto_id: int, direccion: str):
        data = {
            'producto_id': producto_id,
            'direccion_envio': direccion}
        resp = requests.post(f'{self.__URL_MS}/registrar_compra', json=data)
        return resp
        
    def eliminar_compra(self, id_compra: int, observaciones: str):
        datos_observaciones = {'observaciones': observaciones}
        resp = requests.delete(f'{self.__URL_MS}/eliminar_compra/{id_compra}', json=datos_observaciones)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise resp.raise_for_status()
    
    

    