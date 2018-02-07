import peewee  # fades
from playhouse import shortcuts

from siemprelisto.core import db


class Persona(peewee.Model):
    class Meta:
        database = db

    apellido = peewee.CharField()
    nombre = peewee.CharField()

    def __str__(self):
        return '{}, {}'.format(self.apellido, self.nombre)

    def __repr__(self):
        return 'Persona(apellido={}, nombre={})'.format(
            self.apellido,
            self.nombre
        )

    def to_dict(self):
        # TODO Custom json encoder/decoder
        return shortcuts.model_to_dict(self)
