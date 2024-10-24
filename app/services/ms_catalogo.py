import requests
import os
from tenacity import retry, stop_after_attempt , wait_random

def ms_sin_respuesta(retry_state):
    """ Función para cuando falle el último intento \n
     Deuvelve una respuesta con codigo de estado 404 """
    resp = requests.Response()
    resp.status_code = 404
    return resp


class MsCatalogo:

    __URL_MS_CATALOGO = os.getenv('URL_MS_CATALOGO') # Busca la URL en variables de entorno

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3), retry_error_callback=ms_sin_respuesta)
    def get_by_id(self, id: int):
        headers = {'x-proofdock-attack': '{"actions": [{"name": "delay", "value": "10"}]}'}
        resp = requests.get(url=f'{self.__URL_MS_CATALOGO}/get_by_id/{id}', headers=headers)
        return resp