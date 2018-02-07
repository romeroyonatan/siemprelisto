import logging
import json

import falcon

from siemprelisto.core import encoders
from . import models

logger = logging.getLogger(__name__)


class PersonaCollection(object):
    def on_get(self, req, resp):
        # TODO Autenticar y validar
        data = {
            'personas': [
                persona.to_dict() for persona in models.Persona.select()
            ],
        }
        resp.body = json.dumps(data, cls=encoders.JSONEncoder)

    def on_post(self, req, resp):
        # TODO Autenticar y validar
        data = req.media
        persona = models.Persona(**data)
        persona.save()
        resp.body = persona.to_json()
        resp.status = falcon.HTTP_CREATED


class PersonaItem(object):
    def on_get(self, req, resp, uuid):
        # TODO Autenticar y validar
        persona = (
            models
            .Persona
            .select()
            .where(models.Persona.uuid == uuid)
            .get()
        )
        resp.body = persona.to_json()
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, uuid):
        # TODO Autenticar y validar
        data = req.media
        try:
            query = (
                models
                .Persona
                .update(**data)
                .where(models.Persona.uuid == uuid)
            )
        except AttributeError as e:
            logger.exception(e)
            raise falcon.HTTPBadRequest('Bad request', str(e))
        else:
            query.execute()
            persona = (
                models
                .Persona
                .select()
                .where(models.Persona.uuid == uuid)
                .get()
            )
            resp.body = persona.to_json()
            resp.status = falcon.HTTP_OK

    def on_delete(self, req, resp, uuid):
        # TODO Autenticar y validar
        query = models.Persona.delete().where(models.Persona.uuid == uuid)
        deleted = query.execute()
        if deleted == 0:
            raise falcon.HTTPNotFound()
        resp.status = falcon.HTTP_NO_CONTENT
