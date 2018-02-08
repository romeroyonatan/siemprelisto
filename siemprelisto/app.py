# -*- coding: utf-8 -*-
import falcon
import peewee
import voluptuous.error

from .core import db, handlers
from .personas import resources


api = falcon.API(middleware=[
    db.PeeweeConnectionMiddleware(),
])

# Rutas
api.add_route('/personas', resources.PersonaCollection())
api.add_route('/personas/{uuid}', resources.PersonaItem())

# Excepciones
api.add_error_handler(peewee.DoesNotExist,
                      db.handle_does_not_exists)
api.add_error_handler(voluptuous.error.MultipleInvalid,
                      handlers.handle_validation_error)
