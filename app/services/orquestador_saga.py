from saga import SagaBuilder, SagaError
from app.services import MsCatalogo, MsCompras, MsPagos, MsInventario
from app.models import Carrito
import logging

""" Acciones """

class AccionesProcesoCompra:

    def calcular_precio_pago(self, carrito: Carrito):
        """  
        Primera acción del orquetador del proceso de compra de un producto
        (Utiliza el microservicio Catalogo). \n
        Calcula el precio total del carrito y lo define en el parámetro. \n
        En caso de no existir el producto, levanta una excepción.
        """
        ms_catalogo = MsCatalogo()
        producto = ms_catalogo.get_by_id(carrito.producto_id)
        
        # Adjuntamos el precio para el pago del carrito
        carrito.precio_pago = carrito.cantidad * producto.precio

    def registrar_compra(self, carrito: Carrito):
        """ 
        Acción encargada de guardar compra 
        (Utiliza el microservicio Compra). 
        """
        ms_compras = MsCompras()
        datos_compra = ms_compras.registrar_compra(carrito.producto_id, carrito.direccion_envio)
        carrito.compra_id = datos_compra['id'] # Agregamos el id de la compra

    def registrar_pago(self, carrito: Carrito):
        """ 
        Acción encargada de guardar pago
        (Utiliza el microservicio de Pago). 
        """
        ms_pagos = MsPagos()
        datos_pago = ms_pagos.registrar_pago(carrito.producto_id, carrito.precio_pago, carrito.medio_pago)
        carrito.pago_id = datos_pago['id'] # Agregamos el id del pago

    def retirar_stock(self, carrito: Carrito):
        """
        Última acción del orquestador encargada de ingresar un registro de salida del producto en el inventario.
        """
        ms_inventario = MsInventario()
        # Actualizamos inventario con un registro de salida
        resp_info = ms_inventario.egresar_producto(carrito.producto_id, carrito.cantidad)
        if 'Failed' in resp_info.values():
            raise Exception(resp_info['msg'])

        carrito.stock_id = resp_info['id']

        # A modo de prueba, que exista un fallo luego de haber retirado stock
        # raise Exception('Falsa Alarma para testeo')

    """ Acciones compensatorias """

    def nada(self):
        """ Función vacía para cuando no se requiera una compensación en una acción """
        pass


    def eliminar_compra(self, carrito: Carrito):
        """
        Acción compensatoria encargada de eliminar el registro de compra en base al compra_id del carrito
        """
        if carrito.compra_id:
            ms_compras = MsCompras()
            observaciones = 'Motivo de eliminacion: Insuficiente stock o microservicios de Pagos y/o Inventario han fallado.'
            ms_compras.eliminar_compra(carrito.compra_id, observaciones)


    def eliminar_pago(self, carrito: Carrito):
        """
        Acción compensatoria encargada de eliminar el registro de pago en base al pago_id del carrito.
        """
        if carrito.pago_id:
            ms_pagos = MsPagos()
            observaciones = 'Motivo de eliminacion: Insuficiente stock o microservicio de Inventario ha fallado.'
            ms_pagos.eliminar_pago(carrito.pago_id, observaciones)
    
    def reponer_stock(self, carrito: Carrito):
        """
        Acción compensatioria que ingresa (repone) la misma cantidad del carrito al inventario del producto, 
        en caso de que algo falle.
        """
        if carrito.stock_id:
            ms_inventario = MsInventario()
            ms_inventario.ingresar_producto(carrito.producto_id, carrito.cantidad)

class OrquestadorSaga:
    """ 
    Clase orquestadora de procesos \n
    Utiliza la libería saga
    """

    def proceso_compra(self, carrito: Carrito):
        """
        Método en el que se orquesta el proceso de compra de un producto
        """
        acciones = AccionesProcesoCompra() 
        exito = False
        try:
            SagaBuilder \
                .create() \
                .action(lambda: acciones.calcular_precio_pago(carrito), lambda: acciones.nada()) \
                .action(lambda: acciones.registrar_compra(carrito), lambda: acciones.eliminar_compra(carrito)) \
                .action(lambda: acciones.registrar_pago(carrito), lambda: acciones.eliminar_pago(carrito)) \
                .action(lambda: acciones.retirar_stock(carrito), lambda: acciones.reponer_stock(carrito)) \
                .build().execute()
            exito = not exito

        except SagaError as error:
            for e in error.args:
                logging.error(e)

        return exito
    
