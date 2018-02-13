import logging

import falcon

from . import models, utils, validators

logger = logging.getLogger(__name__)


class UserCollection(object):
    def on_get(self, req, resp):
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
        user = models.User.select().filter(id=id).get()
        resp.media = dict(user)
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, id):
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
        query = models.User.delete().where(models.User.id == id)
        deleted = query.execute()
        if deleted == 0:
            raise falcon.HTTPNotFound()
        resp.status = falcon.HTTP_NO_CONTENT


class Login(object):
    auth = {'post': False}  # dont require Authorization

    def on_post(self, req, resp):
        data = req.media
        query = models.User.select().filter(username=data['username'])
        if query.exists():
            user = query.get()
            if user.check_password(data['password']):
                token = utils.get_token(user)
                resp.media = {'token': token}
            else:
                raise falcon.HTTPForbidden()
        else:
            raise falcon.HTTPForbidden()
