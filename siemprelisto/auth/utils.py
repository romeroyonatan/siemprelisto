import datetime
import re

import jwt


from . import models


JWT_SECRET = 'secret'
# JSON Web Token Expiration time (in secs)
JWT_EXPIRATION_TIME = 3600


def is_valid_token(token):
    regex = re.compile(r'[\w.]+')
    if not token or not regex.match(token):
        return False
    try:
        jwt.decode(token, JWT_SECRET)
        return True
    except jwt.InvalidTokenError:
        return False


def get_token(user):
    '''Generate a JSON Web Token for user. '''
    data = {
        'username': user.username,

        # add expiration time
        'exp': datetime.datetime.utcnow() + datetime.timedelta(
            seconds=JWT_EXPIRATION_TIME
        ),
    }
    return jwt.encode(data, key=JWT_SECRET).decode()


def get_user(token):
    '''Get user from token.

    Raise jwt.InvalidTokenError when token is invalid
    '''
    data = jwt.decode(token, JWT_SECRET)
    return models.User.select().filter(username=data['username']).get()
