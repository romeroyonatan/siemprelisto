import peewee

from siemprelisto.core import db


SALT = '5822eaccecb4c721ffee330b21c8ff72882d52a72ae429147226415f66a1a9e4'


class User(db.Model):
    username = peewee.CharField(index=True, unique=True)
    password = peewee.CharField()  # FIXME plaintext password
    apellido = peewee.CharField(null=True)
    nombre = peewee.CharField(null=True)
    email = peewee.CharField(null=True)

    def __str__(self):
        return str(self.username)

    def __iter__(self):
        return (
            (field, getattr(self, field))
            for field in self._meta.fields.keys()
            if field not in ('id', 'password')
        )

    def __repr__(self):
        fields = (
            '{}={!r}'.format(field, getattr(self, field))
            for field in self._meta.fields.keys()
            if field != 'password'
        )
        return '{}({})'.format(type(self).__name__, ', '.join(fields))

    def check_password(self, password):
        return self.password == password

    class Meta:
        database = db.database
