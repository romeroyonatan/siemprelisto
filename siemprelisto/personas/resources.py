import json

import falcon


class Personas(object):

    def on_get(self, req, resp):
        doc = {
            'personas': [
                {
                    'nombre': 'Juan',
                    'apellido': 'Fernandez',
                }
            ]
        }
        resp.body = json.dumps(doc)
