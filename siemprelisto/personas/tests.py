import json

import falcon
import falcon.testing

import pytest

from siemprelisto import app
from siemprelisto.core import db

from . import factory, models


@pytest.fixture
def client():
    return falcon.testing.TestClient(app.api)


@pytest.fixture
def database():
    db.database.connect()
    db.database.create_tables([models.Persona])
    yield db.database
    db.database.drop_tables([models.Persona])
    db.database.close()


def test_lista(client, database):
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
            dict(persona) for persona in personas
        ]
    }
    assert obtenido == esperado


def test_crear(client, database):
    '''Crea una persona nueva'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    data = dict(persona)
    # llamo a la API
    client.simulate_post('/personas', body=json.dumps(data))
    # verifico que exista en la DB
    assert (
        models.Persona
              .select()
              .where(models.Persona.nombre == persona.nombre,
                     models.Persona.apellido == persona.apellido)
              .exists()
    )


def test_respuesta_crear(client, database):
    '''Verifica la respuesta al crear una persona.'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    data = dict(persona)
    # llamo a la API
    response = client.simulate_post('/personas', body=json.dumps(data))
    obtenido = json.loads(response.content)
    assert data['nombre'] == obtenido['nombre']
    assert data['apellido'] == obtenido['apellido']
    assert obtenido['id'] is not None


def test_editar(client, database):
    '''Edita una persona existente'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    persona.save()
    data = dict(persona)
    data['nombre'] = 'Fulano'
    # llamo a la API
    client.simulate_put(
        '/personas/{}'.format(persona.uuid),
        body=json.dumps(data)
    )
    # verifico que se haya modificado en la DB
    assert (
        models.Persona
              .select()
              .where(models.Persona.uuid == persona.uuid,
                     models.Persona.nombre == 'Fulano',
                     models.Persona.apellido == persona.apellido)
              .exists()
    )


def test_respuesta_editar(client, database):
    '''Verifica la respuesta al editar una persona.'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    persona.save()
    data = dict(persona)
    data['nombre'] = 'Fulano'
    # llamo a la API
    response = client.simulate_put(
        '/personas/{}'.format(persona.uuid),
        body=json.dumps(data)
    )
    obtenido = json.loads(response.content)
    persona.nombre = 'Fulano'
    assert dict(persona) == obtenido
    assert response.status == falcon.HTTP_OK


def test_borrar(client, database):
    '''Borra una persona existente'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    persona.save()
    # llamo a la API
    response = client.simulate_delete('/personas/{}'.format(persona.uuid))
    assert response.status == falcon.HTTP_NO_CONTENT
    # verifico que se haya borrado
    assert (
        not models.Persona
                  .select()
                  .where(models.Persona.uuid == persona.uuid)
                  .exists()
    )


def test_consultar(client, database):
    '''Consulta los datos de una persona'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    persona.save()
    # llamo a la API
    response = client.simulate_get('/personas/{}'.format(persona.uuid))
    assert response.status == falcon.HTTP_OK
    # verifico los datos
    obtenido = json.loads(response.content)
    assert dict(persona) == obtenido


def test_actualizar__inexistente(client, database):
    '''Actualizar una persona inexistente'''
    # llamo a la API
    response = client.simulate_put('/personas/12345',
                                   body=json.dumps({'nombre': 'foobar'}))
    assert response.status == falcon.HTTP_NOT_FOUND


def test_actualizar__campos_incorrectos(client, database):
    '''Actualizar una persona con campos incorrectos'''
    # llamo a la API
    response = client.simulate_put('/personas/12345',
                                   body=json.dumps({'foo': 'bar'}))
    assert response.status == falcon.HTTP_BAD_REQUEST


def test_borrar__inexistente(client, database):
    '''Borra una persona inexistente'''
    # llamo a la API
    response = client.simulate_delete('/personas/12345')
    assert response.status == falcon.HTTP_NOT_FOUND


def test_consultar__inexistente(client, database):
    '''Consulta los datos de una persona inexistente'''
    # llamo a la API
    response = client.simulate_get('/personas/1234')
    assert response.status == falcon.HTTP_NOT_FOUND


def test_repr(client, database):
    '''Prueba metodo repr.'''
    persona = factory.PersonaFactory.build()
    persona.save()
    template = "Persona(id={}, uuid='{}', apellido='{}', nombre='{}')"
    assert repr(persona) == template.format(
        persona.id, persona.uuid, persona.apellido, persona.nombre
    )
