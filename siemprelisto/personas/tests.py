import falcon
from falcon import testing
import json
import pytest

from .. import app


@pytest.fixture
def client():
    return testing.TestClient(app.api)


def test_list_images(client):
    doc = {
        'personas': [
            {
                'nombre': 'Juan',
                'apellido': 'Fernandez',
            }
        ]
    }

    response = client.simulate_get('/personas')
    result_doc = json.loads(response.content, encoding='utf-8')

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK
