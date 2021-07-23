from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIRequestFactory

from django_workflow_system.api.tests.factories import (
    WorkflowCollectionAssignmentFactory,
    UserFactory,
    WorkflowCollectionFactory,
    WorkflowCollectionEngagementFactory,
)
from django_workflow_system.api.views.user.workflows import (
    WorkflowCollectionAssignmentsView,
    WorkflowCollectionAssignmentView,
)
from django_workflow_system.models import WorkflowCollectionAssignment


class TestWorkflowAssignmentsView(TestCase):
    def setUp(self):
        self.view = WorkflowCollectionAssignmentsView.as_view()
        self.view_url = "/users/self/workflows/assignments/"
        self.factory = APIRequestFactory()
        self.start = timezone.now()

        self.user = UserFactory()

        self.workflow_collection = WorkflowCollectionFactory()
        self.workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection, user=self.user
        )
        self.workflow_assignment = WorkflowCollectionAssignmentFactory(
            user=self.user,
            workflow_collection=self.workflow_collection,
            engagement=self.workflow_engagement,
        )

        self.workflow_collection_2 = WorkflowCollectionFactory()
        self.workflow_engagement_2 = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection_2, user=self.user
        )
        self.workflow_assignment_2 = WorkflowCollectionAssignmentFactory(
            user=self.user,
            workflow_collection=self.workflow_collection_2,
            engagement=self.workflow_engagement_2,
        )

        self.welcome_assessment = WorkflowCollectionFactory(
            code="demographics_survey_welcome_collection"
        )

    def test_get__expected_payload(self):
        """Verify the payload conforms to expectations."""
        request = self.factory.get(self.view_url)
        request.user = self.user
        response = self.view(request)

        self.assertEqual(len(response.data), 2)

        # Assert Workflow Assignment 1
        self.assertEqual(
            response.data[0]["workflow_collection"],
            f"http://testserver/api/workflow_system/collections/{self.workflow_assignment.workflow_collection.id}/",
        )
        self.assertEqual(
            response.data[0]["start"][0:10], self.start.strftime("%Y-%m-%d")
        )
        self.assertEqual(response.data[0]["status"], "ASSIGNED")
        self.assertEqual(
            response.data[0]["engagement"],
            f"http://testserver/api/workflow_system/users/self/workflows/engagements/{self.workflow_assignment.engagement.id}/",
        )

        # Assert Workflow Assignment 2
        self.assertEqual(
            response.data[1]["workflow_collection"],
            f"http://testserver/api/workflow_system/collections/{self.workflow_assignment_2.workflow_collection.id}/",
        )
        self.assertEqual(
            response.data[1]["start"][0:10], self.start.strftime("%Y-%m-%d")
        )
        self.assertEqual(response.data[1]["status"], "ASSIGNED")
        self.assertEqual(
            response.data[1]["engagement"],
            f"http://testserver/api/workflow_system/users/self/workflows/engagements/{self.workflow_assignment_2.engagement.id}/",
        )


class TestWorkflowAssignmentView(TestCase):
    def setUp(self):
        self.detail_view = WorkflowCollectionAssignmentView.as_view()
        self.factory = APIRequestFactory()
        self.start = timezone.now()

        self.user = UserFactory()
        self.user_2 = UserFactory()
        self.workflow_collection = WorkflowCollectionFactory()
        self.workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection, user=self.user
        )
        self.workflow_assignment = WorkflowCollectionAssignmentFactory(
            user=self.user,
            workflow_collection=self.workflow_collection,
            engagement=self.workflow_engagement,
        )
        self.workflow_assignment_3 = WorkflowCollectionAssignmentFactory(
            user=self.user,
            workflow_collection=self.workflow_collection,
            engagement=self.workflow_engagement,
        )

    def test_get__unauthenticated_detail(self):
        """Unauthenticated users cannot access GET method."""
        request = self.factory.get(
            f"/users/self/workflows/assignments/{self.workflow_assignment.id}/"
        )
        response = self.detail_view(request, self.workflow_assignment)
        self.assertEqual(response.status_code, 403)

    def test_get__authenticated_detail(self):
        """Authenticated users can access GET method."""
        request = self.factory.get(
            f"/users/self/workflows/assignments/{self.workflow_assignment.id}/"
        )
        request.user = self.user
        response = self.detail_view(request, self.workflow_assignment.id)

        self.assertEqual(response.status_code, 200)

    def test_get__success_detail(self):
        """Checking for Assignment returned"""
        request = self.factory.get(
            f"/users/self/workflows/assignments/{self.workflow_assignment.id}/"
        )
        request.user = self.user
        response = self.detail_view(request, self.workflow_assignment.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["workflow_collection"],
            f"http://testserver/api/workflow_system/collections/{self.workflow_assignment.workflow_collection.id}/",
        )
        self.assertEqual(response.data["start"][0:10], self.start.strftime("%Y-%m-%d"))
        self.assertEqual(response.data["status"], self.workflow_assignment.status)
        self.assertEqual(
            response.data["engagement"],
            f"http://testserver/api/workflow_system/users/self/workflows/engagements/{self.workflow_assignment.engagement.id}/",
        )

    def test_get__assignment_id_nonexistent_detail(self):
        """using non-existing workflow ID"""
        made_up_uuiid = "4f84f799-9cc5-43d3-0000-24840b7eb8ce"
        request = self.factory.get(
            "/users/self/workflows/assignments/{}/".format(made_up_uuiid)
        )
        request.user = self.user
        response = self.detail_view(request, made_up_uuiid)

        self.assertEqual(response.status_code, 404)

    def test_get__assignment_does_not_belong_to_user_detail(self):
        """Users Should not have access to others assignments GET method."""
        request = self.factory.get(
            "/users/self/workflows/assignments/{}/".format(self.workflow_assignment.id)
        )
        request.user = self.user_2
        response = self.detail_view(request, self.workflow_assignment.id)

        self.assertEqual(response.status_code, 404)

    def test_patch__valid_payload(self):
        """Patch current target to the one specified."""
        request = self.factory.patch(
            f"/users/self/workflows/assignments/{self.workflow_assignment_3.id}/",
            data={
                "status": "IN_PROGRESS",
                "engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/"
                f"{self.workflow_assignment.engagement.id}/",
            },
            format="json",
        )
        request.user = self.user
        response = self.detail_view(request, self.workflow_assignment_3.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "IN_PROGRESS")
        self.assertEqual(
            response.data["engagement"],
            "http://testserver/api/workflow_system/users/self/workflows/engagements/{}/".format(
                self.workflow_assignment.engagement.id
            ),
        )

    def test_patch__invalid_payload(self):
        """Return 400 Bad Request if attempted patch assignment is invalid."""
        request = self.factory.patch(
            "/users/self/workflows/assignments/{}/".format(self.workflow_assignment.id),
            data={"status": "COMPLETERED"},
            format="json",
        )
        request.user = self.user
        response = self.detail_view(request, self.workflow_assignment.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data, {"status": ['"COMPLETERED" is not a valid choice.']}
        )

    def test_patch__unauthenticated_user(self):
        """Return 403 error for unauthenticated users."""
        request = self.factory.patch(
            f"/users/self/workflows/assignments/{self.workflow_assignment.id}/"
        )
        response = self.detail_view(request, self.workflow_assignment)

        self.assertEqual(response.status_code, 403)

    def test_patch__assignment_does_not_belong_to_user(self):
        """Users should not have access to others assignments GET method."""
        request = self.factory.patch(
            f"/users/self/workflows/assignments/{self.workflow_assignment.id}/",
            data={"status": "ASSIGNED"},
            format="json",
        )
        request.user = self.user_2
        response = self.detail_view(request, self.workflow_assignment_3.id)

        self.assertEqual(response.status_code, 404)

    def test_patch__valid_payload__completed(self):
        """Patch current target to the one specified."""
        wc = WorkflowCollectionFactory()
        wca: WorkflowCollectionAssignment = WorkflowCollectionAssignmentFactory(
            user=self.user,
            workflow_collection=wc,
            engagement=WorkflowCollectionEngagementFactory(
                workflow_collection=wc,
                user=self.user,
                finished=None,
            ),
        )

        request = self.factory.patch(
            f"/users/self/workflows/assignments/{wca.id}/",
            data={
                "status": WorkflowCollectionAssignment.CLOSED_COMPLETE,
            },
            format="json",
        )
        request.user = self.user
        response = self.detail_view(request, wca.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["status"], WorkflowCollectionAssignment.CLOSED_COMPLETE
        )
        self.assertEqual(
            response.data["engagement"],
            f"http://testserver/api/workflow_system/users/self/workflows/engagements/{wca.engagement.id}/",
        )
        wca.refresh_from_db()
        self.assertTrue(wca.engagement.finished)
