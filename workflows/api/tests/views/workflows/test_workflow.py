from django.test import TestCase

from rest_framework.test import APIRequestFactory

from website.api_v2.tests.factories import (
    AuthorFactory, Author2Factory, UserFactory, User2Factory,
    WorkflowFactory, Workflow2Factory, WorkflowStepFactory,
    WorkflowStepVideoFactory)
from website.api_v3.tests import factories
from website.api_v3.views.workflows import (
    WorkflowView, WorkflowsView)


class TestWorkflowsView(TestCase):
    """Test WorkflowsView class."""

    def setUp(self):
        self.view = WorkflowsView.as_view()
        self.factory = APIRequestFactory()

        self.user = UserFactory()
        self.user_2 = User2Factory()
        self.author = AuthorFactory()
        self.author_2 = Author2Factory()
        self.workflow = WorkflowFactory()
        self.workflow_2 = Workflow2Factory()

    def test_get__unauthenticated(self):
        """Unauthenticated users cannot access GET method."""
        request = self.factory.get('/workflows/workflows/')
        response = self.view(request)

        self.assertEqual(response.status_code, 403)

    def test_get__authenticated(self):
        """Authenticated users can access GET method."""
        request = self.factory.get('/workflows/workflows/')
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

    def test_get__success(self):
        """Ensure expected Workflow data is returned."""
        request = self.factory.get('/workflows/workflows/')
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

        # Correct number of workflows are returned
        self.assertEqual(len(response.data), 2)

        for result in response.data:

            # Ensure all expected data parameters are present.
            self.assertListEqual(
                list(result.keys()),
                ["id", "name", "detail", "author", "image"])

            # Validate the content of each returned Workflow
            if result['name'] == self.workflow.name:
                self.assertEqual(
                    result['image'],
                    'http://testserver/media/' + str(self.workflow.image))
                self.assertEqual(
                    result['author']['title'],
                    self.author.title)
                self.assertEqual(
                    result['author']['image'],
                    'http://testserver/media/' + str(self.author.image))
                self.assertEqual(
                    result['author']['user']['first_name'],
                    self.user.first_name)
                self.assertEqual(
                    result['author']['user']['last_name'],
                    self.user.last_name)

            elif result['name'] == self.workflow_2.name:
                self.assertEqual(
                    result['image'],
                    'http://testserver/media/' + str(self.workflow_2.image))
                self.assertEqual(
                    result['author']['title'],
                    self.author_2.title)
                self.assertEqual(
                    result['author']['image'],
                    'http://testserver/media/' + str(self.author_2.image))
                self.assertEqual(
                    result['author']['user']['first_name'],
                    self.user_2.first_name)
                self.assertEqual(
                    result['author']['user']['last_name'],
                    self.user_2.last_name)


class TestWorkflowView(TestCase):
    """Test WorkflowView class."""

    def setUp(self):
        self.view = WorkflowView.as_view()
        self.factory = APIRequestFactory()

        self.user = UserFactory()
        self.author = AuthorFactory()
        self.workflow = WorkflowFactory()
        self.workflow_step = WorkflowStepFactory()
        self.workflow_step_video = WorkflowStepVideoFactory()

    def test_get__unauthenticated(self):
        """Unauthenticated users cannot access GET method."""
        request = self.factory.get(
            '/workflows/workflows/{}/'.format(self.workflow.id))
        response = self.view(request, self.workflow.id)

        self.assertEqual(response.status_code, 403)

    def test_get__authenticated(self):
        """Authenticated users can access GET method."""
        request = self.factory.get(
            '/workflows/workflows/{}/'.format(self.workflow.id))
        request.user = self.user
        response = self.view(request, self.workflow.id)

        self.assertEqual(response.status_code, 200)

    def test_get__success(self):
        """Ensure returned data is as expected."""
        request = self.factory.get(
            '/workflows/workflows/{}/'.format(self.workflow.id))
        request.user = self.user
        response = self.view(request, self.workflow.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], self.workflow.code)
        self.assertEqual(response.data['name'], self.workflow.name)
        self.assertEqual(
            response.data['image'],
            'http://testserver/media/picture.png')
        self.assertEqual(response.data['author']['title'], self.author.title)
        self.assertEqual(
            response.data['author']['image'],
            'http://testserver/media/' + str(self.author.image))
        self.assertEqual(response.data['author']['user']['first_name'],
                         self.user.first_name)
        self.assertEqual(response.data['author']['user']['last_name'],
                         self.user.last_name)
        self.assertEqual(response.data['workflowstep_set'][0]
                         ['workflowstepvideo_set'][0]['ui_identifier'],
                         self.workflow_step_video.ui_identifier)
        self.assertEqual(response.data['workflowstep_set'][0]['code'],
                         self.workflow_step.code)

    def test_get__workflow_id_nonexistent(self):
        """using non-existing workflow ID"""
        made_up_uuiid = '4f84f799-9cc5-43d3-0000-24840b7eb8ce'
        request = self.factory.get(
            '/workflows/workflows/{}/'.format(made_up_uuiid))
        request.user = self.user
        response = self.view(request, made_up_uuiid)

        self.assertEqual(response.status_code, 404)

    def test_no_image(self):
        """test that having no image does not break things"""
        workflow = factories.WorkflowFactory(image=None)
        request = self.factory.get(
            '/workflows/workflows/{}/'.format(workflow.id))
        request.user = self.user
        response = self.view(request, workflow.id)
        self.assertEqual(response.data["image"], None)
