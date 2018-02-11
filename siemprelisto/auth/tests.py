import falcon
import falcon.testing
import jwt
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
    db.database.create_tables([models.User])
    yield db.database
    db.database.drop_tables([models.User])
    db.database.close()


@pytest.fixture
def token(client, database):
    # crea usuario
    user = factory.UserFactory(username='admin', password='admin123')
    user.save()
    data = {'username': 'admin', 'password': 'admin123'}
    # obtiene un token valido
    response = client.simulate_post('/auth/login', json=data)
    return response.json['token']


def test_lista(client, database):
    '''Obtiene la lista de users.'''
    # creo 10 users
    users = factory.UserFactory.build_batch(10)
    for user in users:
        user.save()
    # consulto a la api
    response = client.simulate_get('/auth/users')
    assert response.status == falcon.HTTP_OK
    # verifico que devuelva las users correctamente
    esperado = {
        'users': [
            dict(user) for user in users
        ]
    }
    assert response.json == esperado


def test_crear(client, database):
    '''Crea un usuario nuevo'''
    data = {
        'username': 'foo',
        'password': '12345678',
    }
    # llamo a la API
    client.simulate_post('/auth/users', json=data)
    # verifico que exista en la DB
    assert (
        models.User
              .select()
              .filter(username='foo')
              .exists()
    )


def test_respuesta_crear(client, database):
    '''Verifica la respuesta al crear una user.'''
    # genero una user
    fields = ('nombre', 'apellido', 'username', 'password')
    user = factory.UserFactory.build()
    data = {field: getattr(user, field) for field in fields}
    # llamo a la API
    response = client.simulate_post('/auth/users', json=data)
    obtenido = response.json
    assert data['nombre'] == obtenido['nombre']
    assert data['apellido'] == obtenido['apellido']
    assert data['username'] == obtenido['username']
    assert 'password' not in obtenido


def test_crear__datos_requeridos(client, database):
    '''Prueba validacion campos requeridos'''
    data = {}
    response = client.simulate_post('/auth/users', json=data)
    assert response.status == falcon.HTTP_BAD_REQUEST


def test_borrar(client, database):
    '''Borra una user existente'''
    # genero una user
    user = factory.UserFactory.build()
    user.save()
    # llamo a la API
    response = client.simulate_delete('/auth/users/{}'.format(user.id))
    assert response.status == falcon.HTTP_NO_CONTENT
    # verifico que se haya borrado
    assert (
        not models.User
                  .select()
                  .where(models.User.id == user.id)
                  .exists()
    )


def test_consultar(client, database):
    '''Consulta los datos de una user'''
    # genero una user
    user = factory.UserFactory.build()
    user.save()
    # llamo a la API
    response = client.simulate_get('/auth/users/{}'.format(user.id))
    assert response.status == falcon.HTTP_OK
    # verifico los datos
    assert dict(user) == response.json


def test_editar(client, database):
    '''Edita una user existente'''
    # genero una user
    fields = ('nombre', 'apellido', 'username', 'password')
    user = factory.UserFactory.build()
    user.save()
    data = {field: getattr(user, field) for field in fields}
    data['nombre'] = 'Fulano'
    # llamo a la API
    client.simulate_put(
        '/auth/users/{}'.format(user.id),
        json=data
    )
    # verifico que se haya modificado en la DB
    assert (
        models.User
              .select()
              .where(models.User.id == user.id,
                     models.User.nombre == 'Fulano',
                     models.User.apellido == user.apellido)
              .exists()
    )


def test_respuesta_editar(client, database):
    '''Verifica la respuesta al editar una user.'''
    # genero una user
    fields = ('nombre', 'apellido', 'username', 'password')
    user = factory.UserFactory.build()
    user.save()
    data = {field: getattr(user, field) for field in fields}
    data['nombre'] = 'Fulano'
    # llamo a la API
    response = client.simulate_put(
        '/auth/users/{}'.format(user.id),
        json=data
    )
    user.nombre = 'Fulano'
    assert dict(user) == response.json
    assert response.status == falcon.HTTP_OK


def test_editar__inexistente(client, database):
    '''Actualizar una user inexistente'''
    fields = ('nombre', 'apellido', 'username', 'password')
    user = factory.UserFactory.build()
    data = {field: getattr(user, field) for field in fields}
    # llamo a la API
    response = client.simulate_put('/auth/users/12345', json=data)
    assert response.status == falcon.HTTP_NOT_FOUND


def test_editar__campos_incorrectos(client, database):
    '''Actualizar una user con campos incorrectos'''
    # llamo a la API
    response = client.simulate_put('/auth/users/12345', json={'foo': 'bar'})
    assert response.status == falcon.HTTP_BAD_REQUEST


def test_editar__datos_requeridos(client, database):
    '''Prueba validacion campos requeridos'''
    # genero una user
    user = factory.UserFactory.build()
    user.save()
    data = {'nombre': 'Fulano'}
    response = client.simulate_put('/auth/users/{}'.format(user.id),
                                   json=data)
    assert response.status == falcon.HTTP_BAD_REQUEST


def test_borrar__inexistente(client, database):
    '''Borra una user inexistente'''
    # llamo a la API
    response = client.simulate_delete('/auth/users/12345')
    assert response.status == falcon.HTTP_NOT_FOUND


def test_consultar__inexistente(client, database):
    '''Consulta los datos de una user inexistente'''
    # llamo a la API
    response = client.simulate_get('/auth/users/1234')
    assert response.status == falcon.HTTP_NOT_FOUND


def test_repr(database):
    '''Prueba metodo repr.'''
    user = factory.UserFactory.build()
    user.save()
    template = ("User(id={}, username='{}', apellido='{}', nombre='{}', "
                "email='{}')")
    assert repr(user) == template.format(
        user.id, user.username, user.apellido, user.nombre, user.email,
    )


def test_check_password(database):
    user = factory.UserFactory.build(password='12345678')
    assert user.check_password('12345678')


def test_login__ok(client, database):
    user = factory.UserFactory(username='admin', password='admin123')
    user.save()
    data = {'username': 'admin', 'password': 'admin123'}
    response = client.simulate_post('/auth/login', json=data)
    assert response.status == falcon.HTTP_OK


def test_login_jwt(client, database):
    '''Verifica que el JSON Web Token sea correcto.'''
    user = factory.UserFactory(username='admin', password='admin123')
    user.save()
    data = {'username': 'admin', 'password': 'admin123'}
    response = client.simulate_post('/auth/login', json=data)
    decoded = jwt.decode(response.json['token'], 'secret')
    assert decoded['username'] == 'admin'


def test_login__usuario_inexistente(client, database):
    data = {'username': 'user', 'password': 'user'}
    response = client.simulate_post('/auth/login', json=data)
    assert response.status == falcon.HTTP_FORBIDDEN


def test_login__password_incorrecta(client, database):
    user = factory.UserFactory()
    user.save()
    data = {'username': user.username, 'password': 'admin123'}
    response = client.simulate_post('/auth/login', json=data)
    assert response.status == falcon.HTTP_FORBIDDEN


def test_is_valid_jwt_token(client, token):
    data = {'token': token}
    # verifica si el token es valido
    response = client.simulate_post('/auth/is_valid_token',
                                    json=data)
    assert response.status == falcon.HTTP_OK
    assert response.json['username'] == 'admin'


def test_is_valid_jwt_token__empty(client, token):
    data = {'token': ''}
    response = client.simulate_post('/auth/is_valid_token', json=data)
    assert response.status == falcon.HTTP_BAD_REQUEST


def test_is_valid_jwt_token__bad_chars(client, token):
    data = {'token': '@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'}
    response = client.simulate_post('/auth/is_valid_token', json=data)
    assert response.status == falcon.HTTP_BAD_REQUEST
