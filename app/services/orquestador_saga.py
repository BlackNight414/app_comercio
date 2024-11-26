from saga import SagaBuilder, SagaError
from app.services import MsCatalogo, MsCompras, MsPagos, MsInventario
from app.models import Carrito
import logging
from threading import Lock 

lock = Lock()

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

    def verificar_stock(self, carrito: Carrito):
        """ 
        Acción encargada de verificar el stock del producto a comprar
        (Utiliza el microservicio Inventario) \n
        En caso de haber suficiente stock, prosigue a la siguiente acción. \n
        Sino, levanta una excepción de insuficiencia de stock y se pasa a compensar eliminando pago y compra.
        """
        # Se pide el token, con tiempo de espera
        if lock.acquire(): 
            ms_inventario = MsInventario()
            # Consultamos el stock:
            stock = ms_inventario.consultar_stock(carrito.producto_id)

            # Si el la cantidad del carrito supera el stock, se cancela la compra
            if carrito.cantidad > stock:
                logging.warning(f'Insuficiente stock del producto {carrito.producto_id}')
                lock.release() # Liberamos en caso de no haber suficiente stock
                raise Exception(f'Insuficiente stock del producto {carrito.producto_id}')
        else: # En caso de haberse cumplido el tiempo de espera. Se cancela la compra
            logging.warning('Timeout de acceso del Hilo agotado. Se cancela la compra.')
            raise Exception('Timeout de acceso del Hilo agotado. Se cancela la compra.')

    def retirar_stock(self, carrito: Carrito):
        """
        Última acción del orquestador encargada de ingresar un registro de salida del producto en el inventario.
        """
        ms_inventario = MsInventario()
        # Actualizamos inventario con un registro de salida
        ms_inventario.egresar_producto(carrito.producto_id, carrito.cantidad)

        # A modo de prueba, que exista un fallo luego de haber retirado stock
        # raise Exception('Falsa Alarma para testeo')
        lock.release() # Libera el token

    """ Acciones compensatorias """

    def sin_accion(self):
        """ Función vacía para cuando no se requiera una compensación en una acción """
        pass


    def eliminar_compra(self, carrito: Carrito):
        """
        Acción compensatoria encargada de eliminar el registro de compra en base al compra_id del carrito
        """
        ms_compras = MsCompras()
        observaciones = 'Motivo de eliminacion: Insuficiente stock o microservicios de Pagos y/o Inventario han fallado.'
        ms_compras.eliminar_compra(carrito.compra_id, observaciones)


    def eliminar_pago(self, carrito: Carrito):
        """
        Acción compensatoria encargada de eliminar el registro de pago en base al pago_id del carrito.
        """
        if lock.locked():
            lock.release()

        ms_pagos = MsPagos()
        observaciones = 'Motivo de eliminacion: Insuficiente stock o microservicio de Inventario ha fallado.'
        ms_pagos.eliminar_pago(carrito.pago_id, observaciones)
    
    def reponer_stock(self, carrito: Carrito):
        """
        Acción compensatioria que ingresa (repone) la misma cantidad del carrito al inventario del producto, 
        en caso de que algo falle.
        """
        if lock.locked():
            lock.release()

        ms_inventario = MsInventario()
        ms_inventario.ingresar_producto(carrito.producto_id, carrito.cantidad)

class OrquestadorSaga:
    """ 
    Clase orquestadora de procesos \n
    Utiliza la libería saga
    """

    def proceso_compra(self, carrito: Carrito):
        """
        Método en el que se orquesta el proceso de compre de un producto
        """
        acciones = AccionesProcesoCompra() 
        exito = False
        try:
            SagaBuilder \
                .create() \
                .action(lambda: acciones.calcular_precio_pago(carrito), lambda: acciones.sin_accion()) \
                .action(lambda: acciones.registrar_compra(carrito), lambda: acciones.sin_accion()) \
                .action(lambda: acciones.registrar_pago(carrito), lambda: acciones.eliminar_compra(carrito)) \
                .action(lambda: acciones.verificar_stock(carrito), lambda: acciones.eliminar_pago(carrito)) \
                .action(lambda: acciones.retirar_stock(carrito), lambda: acciones.reponer_stock(carrito)) \
                .build().execute()
            exito = not exito

        except SagaError as error:
            for e in error.args:
                logging.error(e)

        return exito
    
