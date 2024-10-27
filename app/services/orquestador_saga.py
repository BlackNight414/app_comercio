from saga import SagaBuilder, SagaError
from app.services import MsCatalogo, MsCompras, MsPagos, MsInventario
from datetime import date

""" Acciones """

def verificar_existencia_producto(producto_id: int, cantidad: int, fecha_compra: date, medio_pago: str , direccion: str):
    """  
    Primera acción del orquetador del proceso de compra de un producto
    (Utiliza el microservicio Catalogo). \n
    Se encarga de verificar si un producto con id=producto_id existe en la BD.  \n
    En caso de que sí, se devuelve un diccionario con todos los argumentos.
    a la siguiente acción y su correspondiente compensación. \n
    Sino, levanta una excepción alertando la inexistencia del producto. 
    """
    ms_catalogo = MsCatalogo()
    resp = ms_catalogo.get_by_id(producto_id)
    if resp.status_code == 200:
        datos_producto = resp.json()
        # Si no se encontró un producto con ese id, se levanta una excepción.
        if 'NOT FOUND' in datos_producto.values():
            raise Exception(f'No existe el producto con id={producto_id}')
        
        # Devolvemos un diccionario con los datos requeridos para las siguientes acciones
        return {
            'producto_id': producto_id,
            'precio': datos_producto['precio'], # LLevamos el precio del producto para calcular el pago posteriormente
            'cantidad': cantidad,
            'fecha_compra': fecha_compra,
            'medio_pago': medio_pago,
            'direccion': direccion
        }
    else:
        raise Exception('Microservicio Catálogo ha fallado.')

def registrar_compra(**kwargs):
    """ 
    Acción encargada de guardar los datos de compra en la BD 
    (Utiliza el microservicio Compra). 
    """
    ms_compras = MsCompras()
    resp = ms_compras.registrar_compra(kwargs['producto_id'], kwargs['fecha_compra'], kwargs['direccion'])
    if resp.status_code == 200:
        datos_compra = resp.json()
        precio_pago = kwargs['cantidad'] * float(kwargs['precio']) # calculamos el pago total
        kwargs['compra_id'] = datos_compra['id'] # Agregamos el id compra
        kwargs['precio_pago'] = precio_pago # Agregamos el precio total del pago para la siguiente acción
        return kwargs
    else:
        raise Exception('Microservicio Compras ha fallado.')

def registrar_pago(**kwargs):
    """ 
    Acción encargada de guardar los datos de pago en la BD
    (Utiliza el microservicio de Pago). 
    """
    ms_pagos = MsPagos()
    resp = ms_pagos.registrar_pago(kwargs['producto_id'], kwargs['precio_pago'], kwargs['medio_pago'])
    if resp.status_code == 200:
        datos_pago = resp.json()
        kwargs['pago_id'] = datos_pago['id'] # Agregamos el id del pago
        return kwargs
    else:
        raise Exception('Microservicio Pagos ha fallado.')

def verificar_stock(**kwargs):
    """ 
    Acción encargada de verificar el stock del producto a comprar
    (Utiliza el microservicio Inventario) \n
    En caso de haber suficiente stock, prosigue a la siguiente acción, pasando los argumentos recibidos. \n
    Sino, levanta una excepción de insuficiencia de stock y se pasa a compensar eliminando los datos del pago y compra.
    """
    ms_inventario = MsInventario()
    # Consultamos el stock:
    resp_stock = ms_inventario.consultar_stock(kwargs['producto_id'])
    if resp_stock.status_code == 200:
        datos_stock = resp_stock.json()
        stock = float(datos_stock['stock'])

        # Si el la cantidad que desea comprar es menor o igual al stock actual, entonces seguimos
        if stock >= kwargs['cantidad']:
            return kwargs
        else:
            raise Exception(f"Insuficiente stock del producto {kwargs['producto_id']}")

    else:
        raise Exception('Microservicio Inventario - Verificación de stock ha fallado.')

def egresar_stock(**kwargs):
    """
    Última acción del orquestador encargada de actualizar el stock en la BD (Utiliza el microservicio Inventario). \n
    En realidad, inserta un registro de stock en el inventario, como salida del producto.
    Si anduvo bien, se devuelve un mensaje de éxito.
    Sino, se levanta una excepción de fallo del microservicio.
    """
    ms_inventario = MsInventario()
    # Actualizamos inventario con un registro de salida
    resp = ms_inventario.egresar_producto(kwargs['producto_id'], kwargs['fecha_compra'], kwargs['cantidad'])
    if resp.status_code == 200:
        return {'msg': '¡PROCESO DE COMPRA COMPLETADO!'} # retornamos un mensaje de exito (sí o sí un diccionario)
    else:
        raise Exception('Microservicio Inventario - Egreso de stock ha fallado.')

""" Acciones compensatorias """

def nada(**kwargs):
    pass


def eliminar_compra(**kwargs):
    """
    Acción compensatoria encargada de eliminar el registro de compra en base a su id.
    """
    ms_compras = MsCompras()
    observaciones = 'Motivo de eliminacion: Insuficiente stock o microservicios de Pagos y/o Inventario han fallado.'
    ms_compras.eliminar_compra(kwargs['compra_id'], observaciones)


def eliminar_pago(**kwargs):
    """
    Acción compensatoria encargada de eliminar el registro de pago en base a su id.
    """
    ms_pagos = MsPagos()
    observaciones = 'Motivo de eliminacion: Insuficiente stock o microservicio de Inventario ha fallado.'
    ms_pagos.eliminar_pago(kwargs['pago_id'], observaciones)

class OrquestadorSaga:
    """ 
    Clase orquestadora de procesos \n
    Utiliza la libería saga
    """

    def proceso_compra(self , producto_id: int, cantidad: int, fecha_compra: date, medio_pago: str , direccion: str):
        """
        Método en el que se orquesta el proceso de compre de un producto
        """
        exito = False
        try:
            SagaBuilder \
                .create() \
                .action(lambda: verificar_existencia_producto(producto_id, cantidad, fecha_compra, medio_pago, direccion), 
                        lambda: nada()) \
                .action(registrar_compra, nada) \
                .action(registrar_pago, eliminar_compra) \
                .action(verificar_stock, eliminar_pago) \
                .action(egresar_stock, nada) \
                .build().execute()
            exito = not exito

        except SagaError as error:
            for e in error.args:
                print(e)

        return exito
    
