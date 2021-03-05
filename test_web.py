import unittest
from web import app, record


class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tester = app.test_client(cls)

    @classmethod
    def tearDownClass(cls):
        manager = record.get('EUR/USD')
        manager.stop()

    def test_index(self):
        response = self.tester.get('/')
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_record(self):
        response = record.get('EUR/USD')
        response.trade.predict()
        data = response.get_display_data()
        self.assertListEqual(list(data.keys()),['table','close','SMA','EMA', 'accuracy', 'date','model'])

    def test_get_display(self):
        obj = record.get('EUR/USD')
        obj.trade.predict()
        response = self.tester.get('/display/EUR/USD')
        self.assertListEqual(sorted(list(response.json.keys())),
                             sorted(['table','close','SMA','EMA', 'accuracy', 'date','model']))


if __name__ == '__main__':
    unittest.main()

