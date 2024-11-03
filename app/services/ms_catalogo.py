import requests
import os
from tenacity import retry, stop_after_attempt , wait_random

class MsCatalogo:

    __URL_MS = os.getenv('URL_MS_CATALOGO') # Busca la URL en variables de entorno

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def get_by_id(self, id: int):
        # headers = {'x-proofdock-attack': '{"actions": [{"name": "delay", "value": "10"}]}'}
        resp = requests.get(url=f'{self.__URL_MS}/get_by_id/{id}')
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception('Microservicio Catálogo ha fallado.')
    
    def get_all(self):
        resp = requests.get(url=f'{self.__URL_MS}/get_all')
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception('Microservicio Catálogo ha fallado.')