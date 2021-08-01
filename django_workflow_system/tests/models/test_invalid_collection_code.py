from django.core.exceptions import ValidationError
from django.test import TestCase

from ...api.tests.factories.workflows.workflow_collection import (
    WorkflowCollectionFactory,
)
from ...models import WorkflowCollection


class TestWorkflowCollection(TestCase):
    def setUp(self):
        self.workflow_collection = WorkflowCollectionFactory()

    def test_invalid_code_provided(self):
        with self.assertRaises(ValidationError):
            # This should fail, because the code can't contain capitals
            WorkflowCollection.objects.create(
                code="EggsAndBacon",
                version=1,
                name="Eggs and Bacon",
                description="The end",
                ordered=True,
                created_by=self.workflow_collection.created_by,
                category="SURVEY",
                active=True,
            )

        with self.assertRaises(ValidationError):
            # This should fail, because the code cant start with a number
            WorkflowCollection.objects.create(
                code="99_cant_start_with_number",
                version=1,
                name="Eggs and Bacon",
                description="The end",
                ordered=True,
                created_by=self.workflow_collection.created_by,
                category="SURVEY",
                active=True,
            )

        with self.assertRaises(ValidationError):
            # This should fail, because the code can't contain special characters aside from a _
            WorkflowCollection.objects.create(
                code="this_is_close_but_no_sp&c!@LChar^cters",
                version=1,
                name="Eggs and Bacon",
                description="The end",
                ordered=True,
                created_by=self.workflow_collection.created_by,
                category="SURVEY",
                active=True,
            )

        # This'll work
        WorkflowCollection.objects.create(
            code="eggs_and_bacon",
            version=1,
            name="Eggs and Bacon",
            description="The end",
            ordered=True,
            created_by=self.workflow_collection.created_by,
            category="SURVEY",
            active=True,
        )
