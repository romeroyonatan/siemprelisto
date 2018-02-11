import logging
import json

import falcon
import jwt

from siemprelisto.core import encoders
from . import models, validators

logger = logging.getLogger(__name__)


class UserCollection(object):
    def on_get(self, req, resp):
        # TODO Autenticar
        data = {
            'users': [
                dict(user) for user in models.User.select()
            ],
        }
        resp.body = json.dumps(data, cls=encoders.JSONEncoder)

    def on_post(self, req, resp):
        data = validators.validar_user(req.media)
        user = models.User(**data)
        user.save()
        resp.media = dict(user)
        resp.status = falcon.HTTP_CREATED


class UserItem(object):
    def on_get(self, req, resp, id):
        # TODO Autenticar
        user = models.User.select().filter(id=id).get()
        resp.media = dict(user)
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, id):
        # TODO Autenticar
        data = validators.validar_user(req.media)
        query = (
            models
            .User
            .update(**data)
            .where(models.User.id == id)
        )
        query.execute()
        user = models.User.select().filter(id=id).get()
        resp.media = dict(user)
        resp.status = falcon.HTTP_OK

    def on_delete(self, req, resp, id):
        # TODO Autenticar
        query = models.User.delete().where(models.User.id == id)
        deleted = query.execute()
        if deleted == 0:
            raise falcon.HTTPNotFound()
        resp.status = falcon.HTTP_NO_CONTENT


class Login(object):
    def on_post(self, req, resp):
        data = req.media
        query = models.User.select().filter(username=data['username'])
        if query.exists():
            user = query.get()
            if user.check_password(data['password']):
                token = self.generate_jwt(user)
                resp.media = {'token': token.decode()}
            else:
                raise falcon.HTTPForbidden()
        else:
            raise falcon.HTTPForbidden()

    def generate_jwt(self, user):
        '''Generate a JSON Web Token. '''
        return jwt.encode({'username': user.username}, key='secret')


class IsValidToken(object):
    def on_post(self, req, resp):
        token = self.get_token(req)
        try:
            data = jwt.decode(token, 'secret')
            resp.media = data
        except jwt.InvalidTokenError as e:
            logger.exception(e)
            raise falcon.HTTPForbidden()

    def get_token(self, req):
        data = req.media
        token = data['token']
        # TODO validar input
        if not token:
            raise falcon.HTTPBadRequest()
        return token.encode()
