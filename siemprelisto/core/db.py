import logging

import falcon
import peewee

database = peewee.SqliteDatabase('test.db')
logger = logging.getLogger(__name__)


class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        if database.is_closed():
            database.connect()

    def process_response(self, req, resp, resource):
        if not database.is_closed():
            database.close()


def not_exists_handler(ex, req, resp, params):
    '''Handler for NotExists peewee exception. It raises HTTP_NOT_FOUND.'''
    logger.info('Object doest not exists req=%r resp=%r params=%r',
                req, resp, params)
    raise falcon.HTTPNotFound()
