from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status

# from rest_framework.test import APIRequestFactory
#
# from website.api_v3.views.user.workflows import WorkflowCollectionEngagementsView
# import website.api_v3.tests.factories as factories
# from website.workflows.models import WorkflowCollection
#
#
from rest_framework.test import APIRequestFactory

from django_workflow_system.api.tests.factories import (
    UserFactory,
    WorkflowCollectionFactory,
    WorkflowCollectionEngagementFactory,
)
from django_workflow_system.api.views.user.workflows import (
    WorkflowCollectionEngagementsView,
)
from django_workflow_system.models import WorkflowCollection


class TestWorkflowCollectionEngagementsViewFiltering(TestCase):
    view_url = "/users/self/workflows/engagements/"

    def setUp(self):
        self.view = WorkflowCollectionEngagementsView.as_view()
        self.user = UserFactory()
        self.factory = APIRequestFactory()
        self.workflow_collection: WorkflowCollection = WorkflowCollectionFactory(
            **{
                "name": "simple_survey",
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "name": "simple_survey_workflow",
                        "code": "simple_survey_workflow",
                        "workflowstep_set": [
                            {
                                "code": "step1",
                            }
                        ],
                    }
                ],
            }
        )

    def test_default_filter_set(self):
        wce1 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            finished=None,
        )
        wce2 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            finished=timezone.now(),
        )

        request = self.factory.get(self.view_url)
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["detail"],
            f"http://testserver/api/workflow_system/users/self/workflows/engagements/{wce1.id}/",
        )

    def test_include_finished(self):
        wce1 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            finished=None,
        )
        wce2 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            finished=timezone.now(),
        )

        request = self.factory.get(
            self.view_url,
            data={
                "include_finished": True,
            },
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_start_filter(self):
        wce1 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            started=timezone.now(),
        )
        wce2 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            started=timezone.now() - timedelta(10),
        )

        request = self.factory.get(
            self.view_url,
            data={
                "include_finished": True,
                "start": timezone.now() - timedelta(5),
            },
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["detail"],
            f"http://testserver/api/workflow_system/users/self/workflows/engagements/{wce1.id}/",
        )

    def test_end_filter(self):
        wce1 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            started=timezone.now() - timedelta(10),
        )
        wce2 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            started=timezone.now(),
        )

        request = self.factory.get(
            self.view_url,
            data={
                "include_finished": False,
                "end": timezone.now() - timedelta(5),
            },
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["detail"],
            f"http://testserver/api/workflow_system/users/self/workflows/engagements/{wce1.id}/",
        )

    def test_collection_id_filter(self):
        wce1 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            started=timezone.now() - timedelta(10),
        )
        wce2 = WorkflowCollectionEngagementFactory(
            workflow_collection=WorkflowCollectionFactory(),
            user=self.user,
            started=timezone.now(),
        )

        request = self.factory.get(
            self.view_url, data={"collection_id": self.workflow_collection.id}
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["detail"],
            f"http://testserver/api/workflow_system/users/self/workflows/engagements/{wce1.id}/",
        )

    def test_start_end_error(self):
        request = self.factory.get(
            self.view_url,
            data={
                "start": timezone.now(),
                "end": timezone.now() - timedelta(5),
            },
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_type_error(self):
        request = self.factory.get(
            self.view_url,
            data={
                "start": "yesterdayish",
            },
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_collection_id(self):
        request = self.factory.get(
            self.view_url, data={"collection_id": "not_a_real_uuid"}
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_include_details(self):
        wce1 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection,
            user=self.user,
            finished=None,
            workflowcollectionengagementdetail_set=[
                {
                    "step": self.workflow_collection.workflowcollectionmember_set.all()[
                        0
                    ].workflow.workflowstep_set.all()[0]
                }
            ],
        )
        request = self.factory.get(
            self.view_url,
            data={
                "include_details": True,
            },
        )
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("workflowcollectionengagementdetail_set", response.data[0].keys())
