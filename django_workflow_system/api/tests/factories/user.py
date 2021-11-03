import factory
import django.contrib.auth.models as django_models
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    """Factory to create fake users."""

    class Meta:
        model = django_models.User
        django_get_or_create = ("username",)

    username = factory.sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.Faker("password")
    is_staff = False


class StaffUserFactory(UserFactory):
    """Factory to create fake staff users."""

    is_staff = True


__all__ = ["UserFactory", "StaffUserFactory"]
