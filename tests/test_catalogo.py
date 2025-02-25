import unittest
from app import create_app
from app.services import MsCatalogo
from app.models import Producto

class TestMsCatalogo(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.ms_catalogo = MsCatalogo()

    def test_get_by_id(self):
        producto = self.ms_catalogo.get_by_id(1)
        self.assertIsInstance(producto, Producto)

    def test_producto(self):

        datos_producto = {
            'id': 1,
            'nombre': 'Ryzen 3 1200',
            'precio': 15,
            'activado': True
        }

        producto = Producto(**datos_producto)
        self.assertIsInstance(producto, Producto)
        self.assertEqual(producto.id, datos_producto['id'])
        self.assertEqual(producto.nombre, datos_producto['nombre'])
        self.assertEqual(producto.precio, datos_producto['precio'])
        self.assertEqual(producto.activado, datos_producto['activado'])

if __name__ == '__main__':
    unittest.main()