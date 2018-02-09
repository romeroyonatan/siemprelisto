import factory

from . import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    username = factory.Faker('user_name')
    password = factory.Faker('password')
    apellido = factory.Faker('last_name')
    nombre = factory.Faker('first_name')
    email = factory.Faker('free_email')
