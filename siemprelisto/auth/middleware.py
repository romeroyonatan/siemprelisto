import falcon


from . import utils


class AuthenticationMiddleware(object):
    def process_resource(self, req, resp, resource, params):
        ''' Raise Forbidden if JWT Token is invalid in Authorization Header.

        Expected header
        ----------------------------------------
        Authorization: Bearer <token>


        If resource not require authentication, set `auth_required`
        attribute to False
        '''
        if getattr(resource, 'auth_required', True):
            authorization_header = req.auth
            # check if authorizacion header exists
            if not authorization_header:
                raise falcon.HTTPForbidden()

            # check if authorization is Bearer
            if not authorization_header.startswith('Bearer '):
                raise falcon.HTTPForbidden()

            # check if is valid token
            token = authorization_header.split()[-1]
            if not utils.is_valid_token(token):
                raise falcon.HTTPForbidden()
            else:
                req.user = utils.get_user(token)
