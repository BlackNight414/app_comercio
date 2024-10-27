import requests
import os
from tenacity import retry, stop_after_attempt , wait_random

from app.services.ms_sin_respuesta import ms_sin_respuesta

class MsCatalogo:

    __URL_MS = os.getenv('URL_MS_CATALOGO') # Busca la URL en variables de entorno

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3), retry_error_callback=ms_sin_respuesta)
    def get_by_id(self, id: int):
        headers = {'x-proofdock-attack': '{"actions": [{"name": "delay", "value": "10"}]}'}
        resp = requests.get(url=f'{self.__URL_MS}/get_by_id/{id}', headers=headers)
        return resp