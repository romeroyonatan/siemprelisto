# -*- coding: utf-8 -*-
import falcon

from .core import PeeweeConnectionMiddleware
from .personas import resources


api = falcon.API(middleware=[
    PeeweeConnectionMiddleware(),
])

# Rutas
api.add_route('/personas', resources.PersonaCollection())
api.add_route('/personas/{pk}', resources.PersonaItem())
