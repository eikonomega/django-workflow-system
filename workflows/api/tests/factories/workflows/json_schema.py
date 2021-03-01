import factory
from factory.django import DjangoModelFactory

from .....models import JSONSchema


class JSONSchemaFactory(DjangoModelFactory):
    class Meta:
        model = JSONSchema
        django_get_or_create = ("code", "description", "schema")

    code = factory.Sequence(lambda n: "code_{}".format(n))
    description = factory.faker.Faker("paragraph")
    schema = {}


class JSONSchemaOneToFiveFactory(JSONSchemaFactory):

    code = "1_to_5"
    description = "single numerical answer 1 to 5"
    schema = {"type": "number", "enum": [1, 2, 3, 4, 5]}


class JSONSchemaTrueFactory(JSONSchemaFactory):

    code = "always_true"
    description = "Always True"
    schema = {}


__all__ = ["JSONSchemaFactory", "JSONSchemaOneToFiveFactory", "JSONSchemaTrueFactory"]
