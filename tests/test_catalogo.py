import unittest
from app import create_app
from app.services import MsCatalogo

class TestMsCatalogo(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.ms_catalogo = MsCatalogo()

    def test_get_by_id(self):
        resp = self.ms_catalogo.get_by_id(1)
        self.assertEqual(resp.status_code, 200)
        print(resp.json())

    def test_get_all(self):
        resp = self.ms_catalogo.get_all()
        self.assertEqual(resp.status_code, 200)
        print(resp.json())

if __name__ == '__main__':
    unittest.main()