from saga import SagaBuilder, SagaError
from app.services import MsCatalogo, MsCompras, MsPagos, MsInventario
from app.models import Carrito

""" Acciones """

class AccionesProcesoCompra:

    def calcular_precio_pago(self, carrito: Carrito):
        """  
        Primera acción del orquetador del proceso de compra de un producto
        (Utiliza el microservicio Catalogo). \n
        Calcula el precio total del producto y lo define en el parámetro. \n
        En caso de no existir el producto, levanta una excepción.
        """
        ms_catalogo = MsCatalogo()
        datos_producto = ms_catalogo.get_by_id(carrito.producto_id)
        # Si el producto no fue encontrado, se levanta una excepción.
        if 'NOT FOUND' in datos_producto.values():
            raise Exception(f'No existe el producto con id={carrito.producto_id}')
        
        # Adjuntamos el precio para el pago del carrito
        carrito.precio_pago = carrito.cantidad * datos_producto['precio']

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
        ms_inventario = MsInventario()
        # Consultamos el stock:
        datos_stock = ms_inventario.consultar_stock(carrito.producto_id)
        stock = float(datos_stock['stock'])

        # Si el la cantidad del carrito supera el stock, se cancela la compra
        if carrito.cantidad > stock:
            raise Exception(f"Insuficiente stock del producto {carrito.producto_id}")

    def egresar_stock(self, carrito: Carrito):
        """
        Última acción del orquestador encargada de ingresar un registro de salida del producto en el inventario.
        """
        ms_inventario = MsInventario()
        # Actualizamos inventario con un registro de salida
        ms_inventario.egresar_producto(carrito.producto_id, carrito.cantidad)

    """ Acciones compensatorias """

    def nada(self):
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
        ms_pagos = MsPagos()
        observaciones = 'Motivo de eliminacion: Insuficiente stock o microservicio de Inventario ha fallado.'
        ms_pagos.eliminar_pago(carrito.pago_id, observaciones)

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
                .action(lambda: acciones.calcular_precio_pago(carrito), lambda: acciones.nada()) \
                .action(lambda: acciones.registrar_compra(carrito), lambda: acciones.nada()) \
                .action(lambda: acciones.registrar_pago(carrito), lambda: acciones.eliminar_compra(carrito)) \
                .action(lambda: acciones.verificar_stock(carrito), lambda: acciones.eliminar_pago(carrito)) \
                .action(lambda: acciones.egresar_stock(carrito), lambda: acciones.nada()) \
                .build().execute()
            exito = not exito

        except SagaError as error:
            for e in error.args:
                print(e)

        return exito
    
