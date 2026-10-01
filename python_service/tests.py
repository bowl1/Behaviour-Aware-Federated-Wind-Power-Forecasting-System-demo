import json
from unittest.mock import patch

from django.test import Client, SimpleTestCase

from errors import APIError


class APITests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def post(self, path, data):
        return self.client.post(path, json.dumps(data), content_type='application/json')

    def test_health(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok', 'service': 'wind-power-inference'})

    def test_turbine_list_and_lookup(self):
        response = self.client.get('/api/turbines')
        self.assertEqual(response.status_code, 200)
        turbines = response.json()
        self.assertTrue(turbines)
        self.assertEqual([t['id'] for t in turbines], sorted(t['id'] for t in turbines))
        self.assertEqual(set(turbines[0]), {'id', 'name', 'latitude', 'longitude', 'clusterId', 'capacity'})
        self.assertEqual(self.client.get('/api/turbines/' + turbines[0]['id'].lower()).json(), turbines[0])
        self.assertEqual(self.client.get('/api/turbines/missing').status_code, 404)

    @patch('views.predict_24h', return_value=[1.23456] * 24)
    @patch('views.get_model', return_value=(object(), {}, {}))
    def test_forecast_and_predict(self, model, inference):
        turbine = self.client.get('/api/turbines').json()[0]
        request = {'turbineId': turbine['id'].lower(), 'startTime': '2026-10-01T00:00:00Z'}
        response = self.post('/api/forecast', request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'turbineId': turbine['id'], 'clusterId': turbine['clusterId'],
            'predictions': [{'hour': i, 'power': 1.235} for i in range(24)],
        })
        self.assertEqual(inference.call_args.kwargs['capacity_mw'], turbine['capacity'])
        request['clusterId'] = turbine['clusterId']
        response = self.post('/predict', request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(inference.call_args.kwargs['capacity_mw'], 3.0)

    def test_validation_and_methods(self):
        self.assertEqual(self.post('/api/forecast', {}).status_code, 422)
        self.assertEqual(self.post('/predict', {'turbineId': [], 'clusterId': 'bad'}).status_code, 422)
        self.assertEqual(self.post('/api/forecast', []).status_code, 422)
        response = self.client.post('/api/forecast', '{', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get('/predict').status_code, 405)
        self.assertEqual(self.post('/api/forecast', {'turbineId': 'missing', 'startTime': '2026-10-01'}).status_code, 404)
        response = self.post('/predict', {'turbineId': 'T001', 'clusterId': 0, 'startTime': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], 'Invalid startTime format')

    def test_model_errors(self):
        request = {'turbineId': 'T001', 'clusterId': 1, 'startTime': '2026-10-01'}
        self.assertEqual(self.post('/predict', request).status_code, 400)
        with patch('views.get_model', side_effect=APIError(500, 'Model unavailable')):
            response = self.post('/predict', request)
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {'detail': 'Model unavailable'})
        with patch('views.get_model', side_effect=RuntimeError('private details')):
            with self.assertLogs('api', level='ERROR'):
                response = self.post('/predict', request)
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {'detail': 'Internal server error'})

    def test_cors(self):
        response = self.client.options('/api/forecast', HTTP_ORIGIN='http://localhost:5173',
                                       HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
                                       HTTP_ACCESS_CONTROL_REQUEST_HEADERS='content-type')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')
        self.assertIn('content-type', response['Access-Control-Allow-Headers'])
        response = self.client.get('/', HTTP_ORIGIN='http://localhost:5173')
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')
        self.assertNotIn('Access-Control-Allow-Credentials', response)
