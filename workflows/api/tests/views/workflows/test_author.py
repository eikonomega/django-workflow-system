from django.test import TestCase
from rest_framework.exceptions import ErrorDetail

from rest_framework.test import APIRequestFactory

from website.api_v2.tests.factories import (
    AuthorFactory, Author2Factory, UserFactory, WorkflowFactory,
    Workflow2Factory)
from website.api_v3.views.workflows import (
    WorkflowAuthorsView, WorkflowAuthorView)
from website.workflows.models.author import WorkflowAuthor
from website.workflows.models.workflow import Workflow


class TestWorkflowAuthorsView(TestCase):
    """Test WorkflowAuthorsView class."""

    def setUp(self):
        self.view = WorkflowAuthorsView.as_view()
        self.factory = APIRequestFactory()

        self.user = UserFactory()
        self.new_user = UserFactory()
        self.author = AuthorFactory()
        self.author_2 = Author2Factory()
        self.workflow = WorkflowFactory()
        self.workflow_2 = Workflow2Factory()

    def test_get__unauthenticated(self):
        """Unauthenticated users cannot access GET method."""
        request = self.factory.get('/workflows/authors/')
        response = self.view(request)

        self.assertEqual(response.status_code, 403)

    def test_get__authenticated(self):
        """Authenticated users can access GET method."""
        request = self.factory.get('/workflows/authors/')
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

    def test_get__success(self):
        """Checking for authors returned"""
        request = self.factory.get('/workflows/authors/')
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

        # Correct number of authors
        self.assertEqual(len(response.data), 2)

        # Inspect Author 1
        self.assertEqual(
            response.data[0]['title'],
            self.author.title)
        self.assertEqual(
            response.data[0]['image'],
            'http://testserver/media/' + str(self.author.image))
        self.assertEqual(
            response.data[0]['user']['first_name'],
            self.author.user.first_name)
        self.assertEqual(
            response.data[0]['user']['last_name'],
            self.author.user.last_name)

        # Inspect Author 2
        self.assertEqual(
            response.data[1]['title'],
            self.author_2.title)
        self.assertEqual(
            response.data[1]['image'],
            'http://testserver/media/' + str(self.author_2.image))
        self.assertEqual(
            response.data[1]['user']['first_name'],
            self.author_2.user.first_name)
        self.assertEqual(
            response.data[1]['user']['last_name'],
            self.author_2.user.last_name)

    def test_get__no_authors(self):
        """checking for when no authors exist"""
        self.assertEqual(len(WorkflowAuthor.objects.all()), 2)
        Workflow.objects.all().delete()
        WorkflowAuthor.objects.all().delete()
        self.assertEqual(len(WorkflowAuthor.objects.all()), 0)

        request = self.factory.get('/workflows/authors/')
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])


class TestWorkflowAuthorView(TestCase):
    """Test WorkflowAuthorView class."""

    def setUp(self):
        self.view = WorkflowAuthorView.as_view()
        self.factory = APIRequestFactory()

        self.user = UserFactory()
        self.author = AuthorFactory()
        self.workflow = WorkflowFactory()

    def test_get__unauthenticated_detail(self):
        """Unauthenticated users cannot access GET method."""
        request = self.factory.get(
            '/workflows/authors/{}'.format(self.author.id) + '/')
        response = self.view(request)

        self.assertEqual(response.status_code, 403)

    def test_get__authenticated_detail(self):
        """Authenticated users can access GET method."""
        request = self.factory.get(
            '/workflows/authors/{}'.format(self.author.id) + '/')
        request.user = self.user
        response = self.view(request, self.author.id)

        self.assertEqual(response.status_code, 200)

    def test_get__success_detail(self):
        """Valid Author ID returns 200 with appropriate payload."""
        request = self.factory.get(
            '/workflows/authors/{}'.format(self.author.id) + '/')
        request.user = self.user
        response = self.view(request, self.author.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'ruler of all')
        self.assertEqual(
            response.data['image'],
            'http://testserver/media/' + str(self.author.image))
        self.assertEqual(
            response.data['biography'],
            self.author.biography)
        self.assertEqual(
            response.data['user']['first_name'],
            self.author.user.first_name)
        self.assertEqual(
            response.data['user']['last_name'],
            self.author.user.last_name)
        self.assertEqual(
            response.data['workflow_set'][0]['name'],
            self.workflow.name)
        self.assertEqual(
            response.data['workflow_set'][0]['image'],
            'http://testserver/media/' + str(self.workflow.image))

    def test_get__no_author_detail(self):
        """Non-Existent Author ID returns 404."""
        made_up_uuiid = '4f84f799-9cc5-43d3-0000-24840b7eb8ce'
        request = self.factory.get(
            '/workflows/authors/{}/'.format(made_up_uuiid))
        request.user = self.user
        response = self.view(request, made_up_uuiid)

        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(
            response.data,
            {"detail": ErrorDetail(string='Not found.', code='not_found')})
