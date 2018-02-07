import json

import falcon

from . import models


class PersonaCollection(object):
    def on_get(self, req, resp):
        # TODO Autenticar y validar
        data = {
            'personas': [
                persona.to_json() for persona in models.Persona.select()
            ],
        }
        resp.body = json.dumps(data)

    def on_post(self, req, resp):
        # TODO Autenticar y validar
        data = req.media
        persona = models.Persona(**data)
        persona.save()
        resp.body = json.dumps(persona.to_json())
        resp.status = falcon.HTTP_CREATED


class PersonaItem(object):
    def on_put(self, req, resp, pk):
        # TODO Autenticar y validar
        data = req.media
        query = models.Persona.update(**data).where(models.Persona.id == pk)
        query.execute()
        persona = models.Persona.select().where(models.Persona.id == pk).get()
        resp.body = json.dumps(persona.to_json())
        resp.status = falcon.HTTP_OK

    def on_delete(self, req, resp, pk):
        # TODO Autenticar y validar
        query = models.Persona.delete().where(models.Persona.id == pk)
        query.execute()
        resp.status = falcon.HTTP_NO_CONTENT
