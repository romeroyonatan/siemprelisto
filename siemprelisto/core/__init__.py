import peewee  # fades

db = peewee.SqliteDatabase('test.db')


class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        if db.is_closed():
            db.connect()

    def process_response(self, req, resp, resource):
        if not db.is_closed():
            db.close()
