# -*- coding: utf-8 -*-
import falcon
import peewee
import voluptuous.error

from .core import db, handlers

from siemprelisto import auth, personas


api = falcon.API(middleware=[
    db.PeeweeConnectionMiddleware(),
])

# Rutas
api.add_route('/personas', personas.PersonaCollection())
api.add_route('/personas/{uuid}', personas.PersonaItem())

api.add_route('/users', auth.UserCollection())
api.add_route('/users/{id}', auth.UserItem())

# Excepciones
api.add_error_handler(peewee.DoesNotExist,
                      db.handle_does_not_exists)
api.add_error_handler(voluptuous.error.MultipleInvalid,
                      handlers.handle_validation_error)
