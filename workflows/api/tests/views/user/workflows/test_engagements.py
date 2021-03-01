from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIRequestFactory

from website.api_v3.classes import APIResourceCollectionAuthenticationRequiredTestCase
from website.api_v3.views.user.workflows import WorkflowCollectionEngagementsView
import website.api_v3.tests.factories as factories

class TestWorkflowCollectionEngagementsView(APIResourceCollectionAuthenticationRequiredTestCase, TestCase):
    """Test WorkflowEngagementsView."""
    @classmethod
    def setUpTestData(cls):
        cls.maxDiff = 1000
    def setUp(self):
        self.view = WorkflowCollectionEngagementsView.as_view()
        self.view_url = '/users/self/workflows/engagements/'
        self.factory = APIRequestFactory()

        self.user_with_engagement = factories.UserFactory()
        self.user_with_engagement2 = factories.UserFactory()
        self.user_without_engagement = factories.UserFactory(username='Engagementless')

        self.workflow = factories.WorkflowFactory()
        self.workflow2 = factories.WorkflowFactory()

        self.workflow_collection = factories.WorkflowCollectionFactory(
            workflow_set=[
                self.workflow
            ]
        )

        self.workflow_collection2 = factories.WorkflowCollectionFactory(
            workflow_set=[
                self.workflow2
            ]
        )

        self.workflow_step = factories.WorkflowStepFactory(
            workflow=self.workflow
        )
        self.workflow_step2 = factories.WorkflowStepFactory(
            workflow=self.workflow
        )
        self.workflow_step3 = factories.WorkflowStepFactory(
            workflow=self.workflow2,
        )
        self.workflow_user_engagement = factories.WorkflowCollectionEngagementFactory(
            user=self.user_with_engagement,
            workflow_collection=self.workflow_collection,
        )
        self.workflow_user_engagement2 = factories.WorkflowCollectionEngagementFactory(
            user=self.user_with_engagement2,
            workflow_collection=self.workflow_collection2,
        )

        self.workflow_user_engagement_detail = factories.WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=self.workflow_user_engagement2,
            step=self.workflow_step3,
            started=timezone.now(),
            finished=timezone.now())

        # Test needs for previously_completed_workflows
        self.user_with_previous_complete_workflow = factories.UserFactory()
        self.workflow3 = factories.WorkflowFactory.create()
        self.workflow_step4 = factories.WorkflowStepFactory(workflow=self.workflow3)
        self.workflow_collection3 = factories.WorkflowCollectionFactory(
            category='ACTIVITY',
            workflow_set=[self.workflow3]
        )

        self.workflow_collection4 = factories.WorkflowCollectionFactory(
            category='SURVEY',
            workflow_set=[
                self.workflow3,
                self.workflow2,
            ]
        )

        self.engagement = factories.WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection3,
            user=self.user_with_previous_complete_workflow,
            started=timezone.now())
        self.assignment = factories.WorkflowCollectionAssignmentFactory(
            workflow_collection=self.workflow_collection,
            engagement=self.engagement,
            user=self.user_with_engagement,
        )
        self.engagement_detail = factories.WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=self.engagement,
            step=self.workflow_step4,
            started=timezone.now(),
            finished=timezone.now())

        self.engagement.finished = timezone.now()
        self.engagement.save()

        self.engagement2 = factories.WorkflowCollectionEngagementFactory(
            workflow_collection=self.workflow_collection3,
            user=self.user_with_previous_complete_workflow,
            started=timezone.now()
        )
        self.assignment_2 = factories.WorkflowCollectionAssignmentFactory(
            workflow_collection=self.workflow_collection2,
            engagement=self.engagement2,
            user=self.user_with_engagement,
        )

        super(TestWorkflowCollectionEngagementsView, self).setUp()

    def test_get__user_has_no_engagements(self):
        """Return a 200 if requesting user has no engagements."""
        request = self.factory.get(self.view_url)
        request.user = factories.UserFactory()
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data)

    def test_get__user_has_engagements(self):
        """Return engagements for requesting user."""
        request = self.factory.get(self.view_url)
        request.user = self.user_with_engagement
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        for engagement in response.data:
            self.assertListEqual(
                list(engagement.keys()),
                [
                    'detail',
                    'workflow_collection',
                    'started',
                    'finished',
                ]
            )

    def test_post__incomplete_payload(self):
        """Incomplete JSON payload returns a 400 error."""
        request = self.factory.post(self.view_url, data={}, format='json')
        request.user = self.user_without_engagement
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, {
            "workflow_collection": ["This field is required."]})

    def test_post__valid_payload(self):
        """Valid JSON payloads return 201."""
        request = self.factory.post(
            self.view_url,
            data={
                "workflow_collection": 'http://testserver/api_v3/workflows/collections/{}/'.format(
                    self.workflow_user_engagement.workflow_collection.id)},
            format='json')

        request.user = self.user_without_engagement
        response = self.view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(response.data["workflow_collection"], 'http://testserver/api_v3/workflows/collections/{}/'.format(
            self.workflow_user_engagement.workflow_collection.id))
        self.assertEqual(
            response.data['state'],
            {
                "next_step_id": self.workflow_step.id,
                "next_workflow": "http://testserver/api_v3/workflows/workflows/{}/".format(self.workflow_step.workflow.id),
                "prev_workflow": None,
                "prev_step_id": None,
                "previously_completed_workflows": [],
                'steps_completed_in_collection': 0,
                'steps_completed_in_workflow': 0,
                'steps_in_collection': 2,
                'steps_in_workflow': 2,
            })

    def test_post__existing_incomplete_engagement(self):
        """Attempting to recreate an existing engagement results in a 409."""
        request = self.factory.post(
            self.view_url,
            data={
                "workflow_collection":
                    'http://testserver/api_v3/workflows/collections/{}/'.format(
                    self.workflow_user_engagement.workflow_collection.id)
            },
            format='json')
        request.user = self.user_with_engagement
        response = self.view(request)

        self.assertEqual(response.status_code, 409)

    def test_post__finish_before_start(self):
        """
        Attempting to POST a finish date prior to
        a start date results in a 400.
        """
        request = self.factory.post(
            self.view_url,
            data={
                "workflow_collection":
                    'http://testserver/api_v3/workflows/collections/{}/'.format(
                    self.workflow_user_engagement.workflow_collection.id),
                "finished": (
                    self.workflow_user_engagement.started - relativedelta(days=1))},
            format='json')
        request.user = self.user_with_engagement
        response = self.view(request)

        self.assertEqual(response.status_code, 400)

