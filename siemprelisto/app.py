# -*- coding: utf-8 -*-
import falcon
import peewee

from .core import db
from .personas import resources


api = falcon.API(middleware=[
    db.PeeweeConnectionMiddleware(),
])

# Rutas
api.add_route('/personas', resources.PersonaCollection())
api.add_route('/personas/{pk}', resources.PersonaItem())

# Excepciones
api.add_error_handler(peewee.DoesNotExist, db.not_exists_handler)
