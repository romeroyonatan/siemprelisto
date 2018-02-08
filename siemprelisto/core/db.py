import logging
import json

import falcon
import peewee

from . import encoders

database = peewee.SqliteDatabase('test.db')
logger = logging.getLogger(__name__)


class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        if database.is_closed():
            database.connect()

    def process_response(self, req, resp, resource):
        if not database.is_closed():
            database.close()


def handle_does_not_exists(ex, req, resp, params):
    '''Handler for NotExists peewee exception. It raises HTTP_NOT_FOUND.'''
    logger.info('Object doest not exists req=%r resp=%r params=%r',
                req, resp, params)
    raise falcon.HTTPNotFound()


class Model(peewee.Model):
    '''Extiende el modelo de peewee agregando metodos especiales.'''
    def __str__(self):
        return repr(self)

    def __repr__(self):
        fields = (
            '{}={!r}'.format(field, getattr(self, field))
            for field in self._meta.fields.keys()
        )
        return '{}({})'.format(type(self).__name__, ', '.join(fields))

    def __iter__(self):
        return ((field, getattr(self, field))
                for field in self._meta.fields.keys()
                if field != 'id')

    def to_json(self):
        return json.dumps(dict(self), cls=encoders.JSONEncoder)
