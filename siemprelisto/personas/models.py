import json
import uuid

import peewee  # fades
from playhouse import shortcuts

from siemprelisto.core import db, encoders


class Persona(peewee.Model):
    class Meta:
        database = db.database

    uuid = peewee.UUIDField(index=True, unique=True, default=uuid.uuid4)
    apellido = peewee.CharField()
    nombre = peewee.CharField()

    def __str__(self):
        return '{}, {}'.format(self.apellido, self.nombre)

    def __repr__(self):
        return 'Persona(uuid={}, apellido={}, nombre={})'.format(
            self.uuid,
            self.apellido,
            self.nombre
        )

    def to_dict(self):
        return shortcuts.model_to_dict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), cls=encoders.JSONEncoder)
