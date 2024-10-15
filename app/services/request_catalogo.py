import requests
import os

class RequestCatalogo:

    URL_MS_CATALOGO = os.getenv('URL_MS_CATALOGO') # Busca la URL en variables de entorno

    def get_by_id(self, id: int):
        return requests.get(url=f'{self.URL_MS_CATALOGO}/get_by_id/{id}')