# -*- coding: utf-8 -*-
import falcon

from .personas import resources


api = falcon.API()
personas = resources.Personas()
api.add_route('/personas', personas)
