import logging
import json

import falcon

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
        resp.body = user.to_json()
        resp.status = falcon.HTTP_CREATED


class UserItem(object):
    def on_get(self, req, resp, id):
        # TODO Autenticar
        user = models.User.select().filter(id=id).get()
        resp.body = user.to_json()
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
        resp.body = user.to_json()
        resp.status = falcon.HTTP_OK

    def on_delete(self, req, resp, id):
        # TODO Autenticar
        query = models.User.delete().where(models.User.id == id)
        deleted = query.execute()
        if deleted == 0:
            raise falcon.HTTPNotFound()
        resp.status = falcon.HTTP_NO_CONTENT
