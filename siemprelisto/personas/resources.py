import logging
import json

import falcon

from siemprelisto.core import encoders
from . import models, validators

logger = logging.getLogger(__name__)


class PersonaCollection(object):
    def on_get(self, req, resp):
        data = {
            'personas': [
                dict(persona) for persona in models.Persona.select()
            ],
        }
        resp.body = json.dumps(data, cls=encoders.JSONEncoder)

    def on_post(self, req, resp):
        data = validators.validar_persona(req.media)
        persona = models.Persona(**data)
        persona.save()
        resp.body = persona.to_json()
        resp.status = falcon.HTTP_CREATED


class PersonaItem(object):
    def on_get(self, req, resp, uuid):
        persona = models.Persona.select().filter(uuid=uuid).get()
        resp.body = persona.to_json()
        resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, uuid):
        data = validators.validar_persona(req.media)
        query = (
            models
            .Persona
            .update(**data)
            .where(models.Persona.uuid == uuid)
        )
        query.execute()
        persona = models.Persona.select().filter(uuid=uuid).get()
        resp.body = persona.to_json()
        resp.status = falcon.HTTP_OK

    def on_delete(self, req, resp, uuid):
        query = models.Persona.delete().where(models.Persona.uuid == uuid)
        deleted = query.execute()
        if deleted == 0:
            raise falcon.HTTPNotFound()
        resp.status = falcon.HTTP_NO_CONTENT
