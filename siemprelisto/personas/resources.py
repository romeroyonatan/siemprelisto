import logging
import json

import falcon

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
        resp.body = json.dumps(data)

    def on_post(self, req, resp):
        # TODO Autenticar y validar
        data = req.media
        persona = models.Persona(**data)
        persona.save()
        resp.body = json.dumps(persona.to_dict())
        resp.status = falcon.HTTP_CREATED


class PersonaItem(object):
    def on_get(self, req, resp, pk):
        # TODO Autenticar y validar
        persona = models.Persona.select().where(models.Persona.id == pk).get()
        resp.body = json.dumps(persona.to_dict())
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, pk):
        # TODO Autenticar y validar
        data = req.media
        try:
            query = (
                models
                .Persona
                .update(**data)
                .where(models.Persona.id == pk)
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
                .where(models.Persona.id == pk)
                .get()
            )
            resp.body = json.dumps(persona.to_dict())
            resp.status = falcon.HTTP_OK

    def on_delete(self, req, resp, pk):
        # TODO Autenticar y validar
        query = models.Persona.delete().where(models.Persona.id == pk)
        deleted = query.execute()
        if deleted == 0:
            raise falcon.HTTPNotFound()
        resp.status = falcon.HTTP_NO_CONTENT
