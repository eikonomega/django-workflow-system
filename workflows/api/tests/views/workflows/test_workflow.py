from django.test import TestCase
from rest_framework.test import APIRequestFactory

from workflows.api.tests.factories import WorkflowFactory, WorkflowStepFactory
from workflows.api.tests.factories.workflows.step import _WorkflowStepVideoFactory
from workflows.api.views.workflows import WorkflowsView, WorkflowView
from workflows.models import WorkflowAuthor


class TestWorkflowsView(TestCase):
    """Test WorkflowsView class."""

    def setUp(self):
        self.view = WorkflowsView.as_view()
        self.factory = APIRequestFactory()
        self.workflow = WorkflowFactory()
        self.workflow_2 = WorkflowFactory()

    def test_get__success(self):
        """Ensure expected Workflow data is returned."""
        request = self.factory.get('/workflows/workflows/')
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

        # Correct number of workflows are returned
        self.assertEqual(len(response.data), 2)
        for result in response.data:
            # Ensure all expected data parameters are present.
            self.assertListEqual(
                list(result.keys()),
                ["id", "name", "detail", "author", "image"])

            author_obj = WorkflowAuthor.objects.get(id=result['author']["id"])

            # Validate the content of each returned Workflow
            if result['name'] == self.workflow.name:
                self.assertEqual(
                    result['image'],
                    f"http://testserver{str(self.workflow.image)}")
                self.assertEqual(
                    result['author']['title'],
                    author_obj.title)
                self.assertEqual(
                    result['author']['image'],
                    f"http://testserver/{str(author_obj.image)}")
                self.assertEqual(
                    result['author']['user']['first_name'],
                    author_obj.user.first_name)
                self.assertEqual(
                    result['author']['user']['last_name'],
                    author_obj.user.last_name)

            elif result['name'] == self.workflow_2.name:
                self.assertEqual(
                    result['image'],
                    f"http://testserver{str(self.workflow_2.image)}")
                self.assertEqual(
                    result['author']['title'],
                    author_obj.title)
                self.assertEqual(
                    result['author']['image'],
                    f"http://testserver/{str(author_obj.image)}")
                self.assertEqual(
                    result['author']['user']['first_name'],
                    author_obj.user.first_name)
                self.assertEqual(
                    result['author']['user']['last_name'],
                    author_obj.user.last_name)


class TestWorkflowView(TestCase):
    """Test WorkflowView class."""
#
    def setUp(self):
        self.view = WorkflowView.as_view()
        self.factory = APIRequestFactory()

        self.workflow = WorkflowFactory()
        self.workflow_step = WorkflowStepFactory(workflow=self.workflow)
        self.workflow_step_video = _WorkflowStepVideoFactory(workflow_step=self.workflow_step)

    def test_get__success(self):
        """Ensure returned data is as expected."""
        request = self.factory.get(
            f"/workflows/workflows/{self.workflow.id}/")
        response = self.view(request, self.workflow.id)
        print('start')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], self.workflow.code)
        self.assertEqual(response.data['name'], self.workflow.name)
        self.assertEqual(
            response.data['image'],
            f"http://testserver{str(self.workflow.image)}")
        self.assertEqual(response.data['author']['title'], self.workflow.author.title)
        self.assertEqual(
            response.data['author']['image'],
            f"http://testserver/{str(self.workflow.author.image)}")
        self.assertEqual(response.data['author']['user']['first_name'],
                         self.workflow.author.user.first_name)
        self.assertEqual(response.data['author']['user']['last_name'],
                         self.workflow.author.user.last_name)
        self.assertEqual(
            response.data['workflowstep_set'][0]['workflowstepvideo_set'][0]['ui_identifier'],
            self.workflow_step_video.ui_identifier)
        self.assertEqual(response.data['workflowstep_set'][0]['code'],
                         self.workflow_step.code)

    def test_get__workflow_id_nonexistent(self):
        """using non-existing workflow ID"""
        made_up_uuiid = '4f84f799-9cc5-43d3-0000-24840b7eb8ce'
        request = self.factory.get(
            f"/workflows/workflows/{made_up_uuiid}/")
        response = self.view(request, made_up_uuiid)

        self.assertEqual(response.status_code, 404)

    def test_no_image(self):
        """test that having no image does not break things"""
        workflow = WorkflowFactory(image=None)
        request = self.factory.get(
            f"/workflows/workflows/{workflow.id}/")
        response = self.view(request, workflow.id)
        self.assertEqual(response.data["image"], None)
