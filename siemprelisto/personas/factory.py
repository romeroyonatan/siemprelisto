import factory  # fades factory_boy

from . import models


class PersonaFactory(factory.Factory):
    class Meta:
        model = models.Persona

    uuid = factory.Faker('uuid4')
    apellido = factory.Faker('last_name')
    nombre = factory.Faker('first_name')
