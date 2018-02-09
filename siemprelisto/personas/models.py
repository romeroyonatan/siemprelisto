import uuid

import peewee  # fades

from siemprelisto.core import db


class Persona(db.Model):
    uuid = peewee.UUIDField(index=True, unique=True, default=uuid.uuid4)
    apellido = peewee.CharField()
    nombre = peewee.CharField()

    def __str__(self):
        return '{}, {}'.format(self.apellido, self.nombre)

    class Meta:
        database = db.database
