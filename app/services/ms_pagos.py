import requests 
import os

from tenacity import retry, wait_random, stop_after_attempt

class MsPagos:

    __URL_MS_PAGOS = os.getenv('URL_MS_PAGOS')

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def registrar_pago(self, producto_id: int, precio: float, medio_pago: str):
        data = {
            'producto_id': producto_id,
            'precio': precio,
            'medio_pago': medio_pago
        }
        resp = requests.post(f'{self.__URL_MS_PAGOS}/registrar_pago', json=data)
        return resp
        
        """
        if resp.status_code == 200:
            return resp
        else:
            raise Exception
        return resp}
        """
    
    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(3))
    def eliminar_pago(self, pago_id: int):
        resp = requests.delete(f'{self.__URL_MS_PAGOS}/eliminar_pago/{pago_id}')