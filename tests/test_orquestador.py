import unittest
from app import create_app
from app.services import OrquestadorSaga
from app.models import Carrito

class TestProcesoCompraSaga(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def test_proceso_compra_saga(self):
        orquestador = OrquestadorSaga()

        # datos
        datos_carrito = {
            'producto_id': 1,
            'cantidad': 1,
            'medio_pago': 'debito',
            'direccion_envio': 'Calle Falsa 123'
        }

        mi_carrito = Carrito(**datos_carrito)

        exito = orquestador.proceso_compra(mi_carrito)
        self.assertTrue(exito, 'Un proceso del Orquestador ha fallado')


if __name__ == '__main__':
    unittest.main()