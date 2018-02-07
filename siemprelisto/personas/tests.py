import json

import falcon
import falcon.testing

import pytest  # fades

from .. import app, core

from . import factory, models


@pytest.fixture
def client():
    return falcon.testing.TestClient(app.api)


@pytest.fixture
def db():
    core.db.connect()
    core.db.create_tables([models.Persona])
    yield core.db
    core.db.drop_tables([models.Persona])
    core.db.close()


def test_lista(client, db):
    '''Obtiene la lista de personas.'''
    # creo 10 personas
    personas = factory.PersonaFactory.build_batch(10)
    for persona in personas:
        persona.save()
    # consulto a la api
    response = client.simulate_get('/personas')
    assert response.status == falcon.HTTP_OK
    # verifico que devuelva las personas correctamente
    obtenido = json.loads(response.content, encoding='utf-8')
    esperado = {
        'personas': [
            persona.to_json() for persona in personas
        ]
    }
    assert obtenido == esperado


def test_crear(client, db):
    '''Crea una persona nueva'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    data = persona.to_json()
    # llamo a la API
    response = client.simulate_post('/personas', body=json.dumps(data))
    assert response.status == falcon.HTTP_CREATED
    # verifico que exista en la DB
    assert (
        models.Persona
              .select()
              .where(models.Persona.nombre == persona.nombre,
                     models.Persona.apellido == persona.apellido)
              .exists()
    )


def test_editar(client, db):
    '''Edita una persona existente'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    persona.save()
    data = persona.to_json()
    data['nombre'] = 'Fulano'
    # llamo a la API
    response = client.simulate_put(
        '/personas/{}'.format(persona.id),
        body=json.dumps(data)
    )
    assert response.status == falcon.HTTP_OK
    # verifico que se haya modificado en la DB
    assert (
        models.Persona
              .select()
              .where(models.Persona.id == persona.id,
                     models.Persona.nombre == 'Fulano',
                     models.Persona.apellido == persona.apellido)
              .exists()
    )


def test_borrar(client, db):
    '''Borra una persona existente'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    persona.save()
    # llamo a la API
    response = client.simulate_delete('/personas/{}'.format(persona.id))
    assert response.status == falcon.HTTP_NO_CONTENT
    # verifico que se haya borrado
    assert (
        not models.Persona
                  .select()
                  .where(models.Persona.id == persona.id)
                  .exists()
    )
