import logging

import falcon

logger = logging.getLogger(__name__)


def handle_validation_error(ex, req, resp, params):
    '''Maneja errores de validacion. Devuelve Bad request.'''
    logger.warning('Bad request Validation error: %r req=%r resp=%r params=%r',
                   ex, req, resp, params)
    raise falcon.HTTPBadRequest(
        'Bad request',
        ', '.join(str(error) for error in ex.errors)
    )
