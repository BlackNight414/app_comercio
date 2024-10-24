import requests
import os
from datetime import date
from tenacity import retry, stop_after_attempt, wait_random

class MsCompras:

    __URL_MS_COMPRAS = os.getenv('URL_MS_COMPRAS') # Busca la URL en variables de entorno

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def registrar_compra(self, producto_id: int, fecha_compra: date, direccion: str):
        data = {
            'producto_id': producto_id,
            'fecha_compra': fecha_compra.isoformat(),
            'direccion_envio': direccion}
        resp = requests.post(f'{self.__URL_MS_COMPRAS}/registrar_compra', json=data)
        return resp
        

        
        # Si la operación fue correcta
        if resp.status_code == 200:
            return resp.json() # devolvemos el json de compra
        else: # sino, levantamos la excepción
            raise resp.raise_for_status()
    
    def eliminar_compra(self, id_compra: int):
        resp = requests.delete(f'{self.__URL_MS_COMPRAS}/eliminar_compra/{id_compra}')
        if resp.status_code == 200:
            return resp.json()
        else:
            raise resp.raise_for_status()
    
    

    