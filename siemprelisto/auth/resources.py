import datetime
import logging
import re

import falcon
import jwt

from . import models, validators

logger = logging.getLogger(__name__)

JWT_SECRET = 'secret'
# JSON Web Token Expiration time (in secs)
JWT_EXPIRATION_TIME = 3600


class UserCollection(object):
    def on_get(self, req, resp):
        # TODO Autenticar
        resp.media = {
            'users': [
                dict(user) for user in models.User.select()
            ],
        }

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
        data = {
            'username': user.username,

            # add expiration time
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                seconds=JWT_EXPIRATION_TIME
            ),
        }
        return jwt.encode(data, key=JWT_SECRET)


class IsValidToken(object):
    regex = re.compile(r'[\w.]+')

    def on_post(self, req, resp):
        token = self.get_token(req)
        try:
            data = jwt.decode(token, JWT_SECRET)
            resp.media = data
        except jwt.InvalidTokenError as e:
            logger.exception(e)
            raise falcon.HTTPForbidden()

    def get_token(self, req):
        token = req.media.get('token')
        if not token or not self.regex.match(token):
            raise falcon.HTTPBadRequest('Invalid token')
        return token.encode()
