import os
import crud
import unittest
import tempfile


class CrudTestCase(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, crud.app.config['DATABASE'] = tempfile.mkstemp()
        crud.app.testing = True
        self.app = crud.app.test_client()

    def test_Climate(self):
        assert self.app.get('/climate', follow_redirects=False)

    def test_Predict(self):
        assert self.app.get('/climate/predict', follow_redirects=False)

    def test_ClimateWithDataParameter(self):
        abc = self.app.get('/climate', json={
            'rainfall': 200
        })
        json_data = abc.get_json()
        assert json_data


if __name__ == '__main__':
    unittest.main()