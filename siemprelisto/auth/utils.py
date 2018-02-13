import datetime
import re

import jwt


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
    '''Generate a JSON Web Token. '''
    data = {
        'username': user.username,

        # add expiration time
        'exp': datetime.datetime.utcnow() + datetime.timedelta(
            seconds=JWT_EXPIRATION_TIME
        ),
    }
    return jwt.encode(data, key=JWT_SECRET).decode()
