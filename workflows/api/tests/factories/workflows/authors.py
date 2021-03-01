import factory

from ..user import UserFactory
from .....models import WorkflowAuthor


class AuthorFactory(factory.DjangoModelFactory):
    class Meta:
        model = WorkflowAuthor
        django_get_or_create = ('user', 'title')

    user = factory.SubFactory(UserFactory)
    title = factory.Faker('prefix')
    image = 'super-panda.png'
    biography = factory.Faker('paragraph')


__all__ = ["AuthorFactory"]
