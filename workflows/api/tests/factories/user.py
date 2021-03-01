import factory
import django.contrib.auth.models as django_models
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = django_models.User
        django_get_or_create = ("username",)

    username = factory.sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.Faker("password")
    is_staff = False

    # @factory.post_generation
    # def workflowcollectionsubscription_set(self, create, extracted, **kwargs):
    #     if not create or not extracted:
    #         return
    #     from .workflows.subscription import WorkflowCollectionSubscriptionFactory
    #
    #     for workflowcollectionsubscription in extracted:
    #         WorkflowCollectionSubscriptionFactory(
    #             user=self, **workflowcollectionsubscription
    #         )
    #
    # @factory.post_generation
    # def workflowcollectionassignment_set(self, create, extracted, **kwargs):
    #     if not create or not extracted:
    #         return
    #     from .workflows.assignment import WorkflowCollectionAssignmentFactory
    #
    #     for workflowcollectionassignment in extracted:
    #         WorkflowCollectionAssignmentFactory(
    #             user=self, **workflowcollectionassignment
    #         )
    #
    # @factory.post_generation
    # def workflowcollectionengagement_set(self, create, extracted, **kwargs):
    #     if not create or not extracted:
    #         return
    #     from .workflows.engagement import WorkflowCollectionEngagementFactory
    #
    #     for workflowcollectionengagement in extracted:
    #         WorkflowCollectionEngagementFactory(
    #             user=self, **workflowcollectionengagement
    #         )


class StaffUserFactory(UserFactory):
    is_staff = True


__all__ = ["UserFactory", "StaffUserFactory"]
