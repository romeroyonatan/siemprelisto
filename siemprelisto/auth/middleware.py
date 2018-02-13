import falcon


from . import utils


class AuthenticationMiddleware(object):
    def process_resource(self, req, resp, resource, params):
        ''' Raise Forbidden if JWT Token is invalid in Authorization Header.

        Expected header
        ----------------------------------------
        Authorization: Bearer <token>


        If resource not require authentication, set `auth` dict with method
        to False (Its true by default.)

        ```
        class Resource:
            auth = {'get': False}
            def on_get(self, req, resp):
                'Dont need auth.'
                pass

            def on_post(self, req, resp):
                'Need auth.'
                pass
        ```
        '''
        auth_map = getattr(resource, 'auth', {})
        if auth_map.get(req.method, True):
            authorization_header = req.auth
            # check if authorizacion header exists
            if not authorization_header:
                raise falcon.HTTPForbidden()

            # check if authorization is Bearer
            if not authorization_header.startswith('Bearer '):
                raise falcon.HTTPForbidden()

            # check if is valid token
            token = authorization_header.split()[-1]
            if utils.is_valid_token(token):
                req.user = utils.get_user(token)
            else:
                raise falcon.HTTPForbidden()
