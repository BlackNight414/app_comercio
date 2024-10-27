import unittest
from app import create_app
from app.services import OrquestadorSaga
from datetime import date

class TestProcesoCompraSaga(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def test_proceso_compra_saga(self):
        orquestador = OrquestadorSaga()

        # datos
        producto_id = 1
        cantidad = 1
        fecha_compra = date.fromisoformat('2024-10-27')
        medio_pago = 'debito'
        direccion = 'Calle Falsa 123'

        exito = orquestador.proceso_compra(producto_id, cantidad, fecha_compra, medio_pago, direccion)
        self.assertTrue(exito, 'Un proseco del Orquestador ha fallado')


if __name__ == '__main__':
    unittest.main()