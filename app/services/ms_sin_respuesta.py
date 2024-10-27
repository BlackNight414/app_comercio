import requests

def ms_sin_respuesta(retry_state):
    """ Función para cuando falle el último intento \n
     Deuvelve una respuesta con codigo de estado 404 """
    resp = requests.Response()
    resp.status_code = 404
    return resp