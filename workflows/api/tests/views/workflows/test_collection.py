from django.test import TestCase

from rest_framework.test import APIRequestFactory

from website.api_v2.tests.factories import (
    UserFactory,
    WorkflowCollectionFactory,
    WorkflowCollectionMemberFactory,
    WorkflowCollectionMember2Factory,
    WorkflowCollection2Factory,
    WorkflowTagOptionFactory,
    WorkflowFactory,
)
from website.api_v3.views.workflows.collection import (
    WorkflowCollectionsView,
    WorkflowCollectionView,
)
from ... import factories

class TestWorkflowCollectionsView(TestCase):
    """Test WorkflowCollectionsView class."""

    def setUp(self):
        self.view = WorkflowCollectionsView.as_view()
        self.factory = APIRequestFactory()

        self.user = UserFactory()
        self.workflow_collection = WorkflowCollectionFactory()
        self.workflow_collection_member = WorkflowCollectionMemberFactory()
        self.workflow_collection_2 = WorkflowCollection2Factory()
        self.workflow_collection_member_2 = WorkflowCollectionMember2Factory()

        self.workflow_collection_tag_option = WorkflowTagOptionFactory()
        self.workflow_collection_tag_option2 = WorkflowTagOptionFactory(
            text="Wilder and crazier tag"
        )
        self.workflow_collection_tag_option3 = WorkflowTagOptionFactory(
            text="Wildest and craziest tag"
        )

        self.workflow_collection.tags.add(self.workflow_collection_tag_option)

        self.workflow_collection_2.tags.add(
            self.workflow_collection_tag_option2, self.workflow_collection_tag_option3,
        )

    def test_get__unauthenticated(self):
        """Unauthenticated users cannot access GET method."""
        request = self.factory.get("/workflows/collections/")
        response = self.view(request)

        self.assertEqual(response.status_code, 403)

    def test_get__authenticated(self):
        """Authenticated users can access GET method."""
        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

    def test_get__success(self):
        """Checking for workflow collection members returned"""
        request = self.factory.get("/workflows/collections/")
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data[1]["tags"]), 2)
        for result in response.data:
            self.assertListEqual(
                list(result.keys()),
                [
                    "id",
                    "detail",
                    "code",
                    "version",
                    "active",
                    "created_date",
                    "modified_date",
                    "description",
                    "detail_image",
                    "home_image",
                    "library_image",
                    "assignment_only",
                    "name",
                    "ordered",
                    "authors",
                    "category",
                    "tags",
                    "newer_version",
                ],
            )

        self.assertEqual(response.data[0]["code"], self.workflow_collection.code)
        self.assertEqual(response.data[0]["name"], self.workflow_collection.name)
        self.assertEqual(response.data[0]["ordered"], self.workflow_collection.ordered)
        self.assertEqual(
            response.data[0]["category"], self.workflow_collection.category
        )
        self.assertEqual(
            response.data[0]["tags"][0], self.workflow_collection_tag_option.text
        )

        self.assertEqual(response.data[1]["code"], self.workflow_collection_2.code)
        self.assertEqual(response.data[1]["name"], self.workflow_collection_2.name)
        self.assertEqual(
            response.data[1]["ordered"], self.workflow_collection_2.ordered
        )
        self.assertEqual(
            response.data[1]["category"], self.workflow_collection_2.category
        )
        self.assertEqual(
            response.data[1]["authors"][0]["user"]["first_name"], self.user.first_name
        )
        self.assertEqual(
            response.data[1]["authors"][0]["user"]["last_name"], self.user.last_name
        )
        self.assertEqual(
            response.data[1]["tags"][0], self.workflow_collection_tag_option2.text
        )
        self.assertEqual(
            response.data[1]["tags"][1], self.workflow_collection_tag_option3.text
        )


class TestWorkflowCollectionView(TestCase):
    """Test WorkflowCollectionView class."""

    @classmethod
    def setUpTestData(cls):
        cls.simple_survey__survey_collection = factories.WorkflowCollectionFactory(**{
            "name": "simple_survey",
            "category": "SURVEY",
            "workflow_set": [{
                "name": "simple_survey_workflow",
                "code": "simple_survey_workflow",
                "workflowstep_set": [
                    {
                        "code": "step1",
                    },
                ]
            }]
        })

        cls.workflow = WorkflowFactory()
        cls.workflow_collection = WorkflowCollectionFactory()
        cls.workflow_collection_member = WorkflowCollectionMemberFactory()

        cls.workflow_collection_tag_option = WorkflowTagOptionFactory()
        cls.workflow_collection.tags.add(cls.workflow_collection_tag_option)

    def setUp(self):
        self.view = WorkflowCollectionView.as_view()
        self.factory = APIRequestFactory()
        self.user = UserFactory()

    def test_get__unauthenticated(self):
        """Unauthenticated users cannot access GET method."""
        request = self.factory.get(
            "/workflows/collections/{}/".format(self.workflow_collection.id)
        )
        response = self.view(request, self.workflow_collection.id)

        self.assertEqual(response.status_code, 403)

    def test_get__authenticated(self):
        """Authenticated users can access GET method."""
        request = self.factory.get(
            "/workflows/collections/{}/".format(self.workflow_collection.id)
        )
        request.user = self.user
        response = self.view(request, self.workflow_collection.id)

        self.assertEqual(response.status_code, 200)

    def test_get__success(self):
        """Ensure response payload is as expected."""
        request = self.factory.get(
            "/workflows/collections/{}/".format(self.workflow_collection.id)
        )
        request.user = self.user
        response = self.view(request, self.workflow_collection.id)

        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.data.keys()),
            [
                "self_detail",
                "id",
                "code",
                "version",
                "active",
                "created_date",
                "modified_date",
                "description",
                "detail_image",
                "home_image",
                "library_image",
                "assignment_only",
                "name",
                "ordered",
                "workflowcollectionmember_set",
                "authors",
                "category",
                "tags",
                "newer_version",
            ],
        )

        self.assertEqual(response.data["code"], self.workflow_collection.code)
        self.assertEqual(response.data["name"], self.workflow_collection.name)
        self.assertEqual(response.data["ordered"], self.workflow_collection.ordered)
        self.assertEqual(response.data["category"], self.workflow_collection.category)
        self.assertEqual(
            response.data["workflowcollectionmember_set"][0]["workflow"]["detail"],
            "http://testserver/api_v3/workflows/workflows/{}/".format(self.workflow.id),
        )
        self.assertEqual(
            response.data["workflowcollectionmember_set"][0]["order"],
            self.workflow_collection_member.order,
        )
        self.assertEqual(
            response.data["authors"][0]["user"]["first_name"], self.user.first_name
        )
        self.assertEqual(
            response.data["authors"][0]["user"]["last_name"], self.user.last_name
        )
        self.assertEqual(
            response.data["tags"][0], self.workflow_collection_tag_option.text
        )

    def test_get__nonexistent_workflow_collection(self):
        """Attempts to retrieve a non-existent collection result in a 404."""
        made_up_uuiid = "4f84f799-9cc5-43d3-0000-24840b7eb8ce"
        request = self.factory.get("/workflows/collections/{}/".format(made_up_uuiid))
        request.user = self.user
        response = self.view(request, made_up_uuiid)

        self.assertEqual(response.status_code, 404)

    def test_get_include_steps__success(self):
        """Ensure response payload is as expected."""
        request = self.factory.get(
            "/workflows/collections/{}/".format(self.simple_survey__survey_collection.id),
            data={"include_steps":"true"}
        )
        request.user = self.user
        response = self.view(request, self.simple_survey__survey_collection.id)

        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.data.keys()),
            [
                "self_detail",
                "id",
                "code",
                "version",
                "active",
                "created_date",
                "modified_date",
                "description",
                "detail_image",
                "home_image",
                "library_image",
                "assignment_only",
                "name",
                "ordered",
                "workflowcollectionmember_set",
                "authors",
                "category",
                "tags",
                "newer_version",
            ],
        )
        self.assertEqual(len(response.data["workflowcollectionmember_set"]), 1)
        for workflow_collection_member in response.data["workflowcollectionmember_set"]:
            self.assertListEqual(
                list(workflow_collection_member.keys()),
                [
                    'order',
                    'workflow'
                ]
            )
            workflow = workflow_collection_member["workflow"]
            self.assertListEqual(
                list(workflow.keys()),
                [
                    'id',
                    'detail',
                    'code',
                    'name',
                    'image',
                    'author',
                    'workflowstep_set'
                ]
            )
            workflow_step_set = workflow["workflowstep_set"]
            self.assertEqual(len(workflow_step_set), 1)
            for step in workflow_step_set:
                self.assertListEqual(
                    list(step.keys()),
                    [
                        "id",
                        'code',
                        "order",
                        "ui_template",
                        "workflowstepinput_set",
                        "workflowsteptext_set",
                        "workflowstepaudio_set",
                        "workflowstepimage_set",
                        "workflowstepvideo_set",
                    ]
                )

    def test_get_include_steps__fail(self):
        """Ensure response payload is as expected."""
        request = self.factory.get(
            "/workflows/collections/{}/".format(self.simple_survey__survey_collection.id),
            data={"include_steps":"beef"}
        )
        request.user = self.user
        response = self.view(request, self.simple_survey__survey_collection.id)

        self.assertEqual(response.status_code, 400)
