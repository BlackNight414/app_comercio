from app.services import MsCatalogo, MsCompras, MsPagos, MsInventario
from datetime import date 

class OrquestadorManual:

    # Funcionalidad de compra de producto
    def comprar_producto(self, producto_id: int, cantidad: int, medio_pago: str , direccion: str):
        ms_catalogo = MsCatalogo()
        ms_compras = MsCompras()
        ms_pagos = MsPagos()
        ms_inventario = MsInventario()
        
        # Verificamos si existe el producto por su id
        resp_catalogo = ms_catalogo.get_by_id(producto_id)
        print('Respuesta catalogo: ', resp_catalogo.status_code)
        if resp_catalogo.status_code == 200:

            datos_producto = resp_catalogo.json()
            
            # Compramos el producto
            resp_compra = ms_compras.registrar_compra(producto_id, direccion)
            print('Respuesta POST compra: ', resp_compra.status_code)
            if resp_compra.status_code == 200:
                
                datos_compra = resp_compra.json()
                precio_pago = cantidad * datos_producto['precio'] # precio a pagar de la compra (dependiendo de la cantidad a comprar)

                # Agregamos el pago
                resp_pagos = ms_pagos.registrar_pago(datos_compra['producto_id'], precio_pago, medio_pago)
                print('Respuesta POST pago: ', resp_pagos.status_code)
                if resp_pagos.status_code == 200:

                    datos_pago = resp_pagos.json()
                    # Verificamos el stock del producto
                    resp_stock = ms_inventario.consultar_stock(producto_id)
                    print('Respuesta GET inventario: ', resp_stock.status_code)
                    stock = float(resp_stock.json()['stock'])

                    if stock>cantidad: 
                        # Si el stock es mayor a la cantidad comprada, entonces despachamos
                        resp_inventario = ms_inventario.egresar_producto(producto_id, cantidad)
                        print('Respuesta POST inventario: ', resp_inventario.status_code)

                        if resp_inventario.status_code == 200:
                            return '¡Proceso de Compra exitoso!'
                        else:
                            # Si la operacion no fue exitosa, entonces compensamos las anteriores
                            ms_pagos.eliminar_pago(datos_pago['id'])
                            ms_compras.eliminar_compra(datos_compra['id'])
                            raise Exception('Microservicio de Inventario ha fallado')

                    else:
                        ms_pagos.eliminar_pago(datos_pago['id'])
                        ms_compras.eliminar_compra(datos_compra['id'])
                        raise Exception('No hay suficiente stock')
                
                else: # Si el pago no fue exitoso
                    ms_compras.eliminar_compra(datos_compra['id'])
                    raise Exception('Microservicio de Pago ha fallado')
            
            else:
                raise Exception('Microservico de Compra ha fallado')
            
        else:
            raise Exception('Microservicio de Catalogo ha fallado')