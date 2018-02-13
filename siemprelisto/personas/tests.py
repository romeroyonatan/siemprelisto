import falcon
import falcon.testing

import pytest

from siemprelisto import app
from siemprelisto.core import db
from siemprelisto import auth

from . import factory, models


@pytest.fixture
def database():
    db.database.connect()
    db.database.create_tables([models.Persona, auth.models.User])
    yield db.database
    db.database.drop_tables([models.Persona, auth.models.User])
    db.database.close()


@pytest.fixture
def token(database):
    # crea usuario
    user = auth.factory.UserFactory(username='admin', password='admin123')
    user.save()
    return auth.utils.get_token(user)


@pytest.fixture
def client(token):
    return falcon.testing.TestClient(app.api, headers={
        'Authorization': 'Bearer ' + token
    })


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
    esperado = {
        'personas': [
            dict(persona) for persona in personas
        ]
    }
    assert response.json == esperado


def test_crear(client, database):
    '''Crea una persona nueva'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    data = {field: getattr(persona, field) for field in ('nombre', 'apellido')}
    # llamo a la API
    client.simulate_post('/personas', json=data)
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
    data = {field: getattr(persona, field) for field in ('nombre', 'apellido')}
    # llamo a la API
    response = client.simulate_post('/personas', json=data)
    obtenido = response.json
    assert data['nombre'] == obtenido['nombre']
    assert data['apellido'] == obtenido['apellido']
    assert obtenido['uuid'] is not None


def test_crear__datos_requeridos(client, database):
    '''Prueba validacion campos requeridos'''
    data = {}
    response = client.simulate_post('/personas', json=data)
    assert response.status == falcon.HTTP_BAD_REQUEST


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
    assert dict(persona) == response.json


def test_editar(client, database):
    '''Edita una persona existente'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    persona.save()
    data = {field: getattr(persona, field) for field in ('nombre', 'apellido')}
    data['nombre'] = 'Fulano'
    # llamo a la API
    client.simulate_put(
        '/personas/{}'.format(persona.uuid),
        json=data
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
    data = {field: getattr(persona, field) for field in ('nombre', 'apellido')}
    data['nombre'] = 'Fulano'
    # llamo a la API
    response = client.simulate_put(
        '/personas/{}'.format(persona.uuid),
        json=data
    )
    persona.nombre = 'Fulano'
    assert dict(persona) == response.json
    assert response.status == falcon.HTTP_OK


def test_editar__inexistente(client, database):
    '''Actualizar una persona inexistente'''
    persona = factory.PersonaFactory.build()
    persona.save()
    data = {field: getattr(persona, field) for field in ('nombre', 'apellido')}
    # llamo a la API
    response = client.simulate_put('/personas/12345', json=data)
    assert response.status == falcon.HTTP_NOT_FOUND


def test_editar__campos_incorrectos(client, database):
    '''Actualizar una persona con campos incorrectos'''
    # llamo a la API
    response = client.simulate_put('/personas/12345', json={'foo': 'bar'})
    assert response.status == falcon.HTTP_BAD_REQUEST


def test_editar__datos_requeridos(client, database):
    '''Prueba validacion campos requeridos'''
    # genero una persona
    persona = factory.PersonaFactory.build()
    persona.save()
    data = {'nombre': 'Fulano'}
    response = client.simulate_put('/personas/{}'.format(persona.uuid),
                                   json=data)
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
