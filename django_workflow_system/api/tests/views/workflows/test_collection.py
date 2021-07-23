from django.conf import settings
from django.test import TestCase

from rest_framework.test import APIRequestFactory

from django_workflow_system.api.tests.factories import (
    UserFactory,
    WorkflowCollectionFactory,
    WorkflowFactory,
)
from django_workflow_system.api.tests.factories.workflows import (
    WorkflowCollectionImageTypeFactory,
    WorkflowCollectionImageFactory,
)
from django_workflow_system.api.tests.factories.workflows.workflow_collection import (
    _WorkflowCollectionMemberFactory,
)
from django_workflow_system.api.tests.factories.workflows.metadata import (
    WorkflowMetadataFactory,
)
from django_workflow_system.api.views.workflows import (
    WorkflowCollectionsView,
    WorkflowCollectionView,
)


class TestWorkflowCollectionsView(TestCase):
    """Test WorkflowCollectionsView class."""

    def setUp(self):
        self.view = WorkflowCollectionsView.as_view()
        self.factory = APIRequestFactory()
        self.user = UserFactory()

        self.workflow_metadata_1 = WorkflowMetadataFactory(
            name="Eggs", description="Chicken Product"
        )
        self.workflow_metadata_2 = WorkflowMetadataFactory(
            name="Bacon", description="Pork Product"
        )

        # WORKFLOW COLLECTION 1
        self.workflow_collection = WorkflowCollectionFactory()
        self.workflow_collection.metadata.add(self.workflow_metadata_1)

        # WORKFLOW COLLECTION 2
        self.workflow_collection_2 = WorkflowCollectionFactory()
        self.workflow_collection_2.metadata.add(self.workflow_metadata_2)
        # IMAGES
        self.workflow_collection_image_type = WorkflowCollectionImageTypeFactory(
            type="Detail"
        )
        self.workflow_collection_image_type_2 = WorkflowCollectionImageTypeFactory(
            type="Homepage"
        )
        self.workflow_collection_image = WorkflowCollectionImageFactory(
            type=self.workflow_collection_image_type,
            image=settings.MEDIA_ROOT + "/wumbo.jpg",
            collection=self.workflow_collection,
        )
        self.workflow_collection_image_2 = WorkflowCollectionImageFactory(
            type=self.workflow_collection_image_type_2,
            image=settings.MEDIA_ROOT + "/wumbo2.jpg",
            collection=self.workflow_collection,
        )
        self.workflow_collection_image_3 = WorkflowCollectionImageFactory(
            type=self.workflow_collection_image_type,
            image=settings.MEDIA_ROOT + "/wumbo3.jpg",
            collection=self.workflow_collection_2,
        )

        self.image_1_dict = {
            "image_url": f"http://testserver{self.workflow_collection_image.image.url}",
            "image_type": self.workflow_collection_image.type.type,
        }
        self.image_2_dict = {
            "image_url": f"http://testserver{self.workflow_collection_image_2.image.url}",
            "image_type": self.workflow_collection_image_2.type.type,
        }
        self.image_3_dict = {
            "image_url": f"http://testserver{self.workflow_collection_image_3.image.url}",
            "image_type": self.workflow_collection_image_3.type.type,
        }

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
                    "assignment_only",
                    "recommendable",
                    "name",
                    "ordered",
                    "authors",
                    "images",
                    "category",
                    "metadata",
                    "newer_version",
                    "dependencies_completed",
                ],
            )

        self.assertEqual(response.data[0]["code"], self.workflow_collection.code)
        self.assertEqual(response.data[0]["name"], self.workflow_collection.name)
        self.assertEqual(response.data[0]["ordered"], self.workflow_collection.ordered)
        self.assertEqual(
            response.data[0]["category"], self.workflow_collection.category
        )
        self.assertEqual(response.data[0]["metadata"][0][0], "Eggs")

        self.assertCountEqual(
            response.data[0]["images"], [self.image_1_dict, self.image_2_dict]
        )

        self.assertEqual(response.data[1]["code"], self.workflow_collection_2.code)
        self.assertEqual(response.data[1]["name"], self.workflow_collection_2.name)
        self.assertEqual(
            response.data[1]["ordered"], self.workflow_collection_2.ordered
        )
        self.assertEqual(
            response.data[1]["category"], self.workflow_collection_2.category
        )

        self.assertCountEqual(response.data[1]["images"], [self.image_3_dict])
        self.assertEqual(response.data[1]["metadata"][0][0], "Bacon")


class TestWorkflowCollectionView(TestCase):
    """Test WorkflowCollectionView class."""

    def setUp(self):
        self.view = WorkflowCollectionView.as_view()
        self.factory = APIRequestFactory()

        self.simple_survey__survey_collection = WorkflowCollectionFactory(
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
                            },
                        ],
                    }
                ],
            }
        )

        self.user = UserFactory()

        self.workflow = WorkflowFactory()
        self.workflow_collection = WorkflowCollectionFactory()
        self.workflow_collection_member = _WorkflowCollectionMemberFactory(
            workflow=self.workflow, workflow_collection=self.workflow_collection
        )

        self.workflow_metadata_1 = WorkflowMetadataFactory(
            name="Eggs", description="Chicken Product"
        )
        self.workflow_collection.metadata.add(self.workflow_metadata_1)
        # IMAGE
        self.workflow_collection_image_type = WorkflowCollectionImageTypeFactory(
            type="Detail"
        )
        self.workflow_collection_image_type_2 = WorkflowCollectionImageTypeFactory(
            type="Homepage"
        )
        self.workflow_collection_image = WorkflowCollectionImageFactory(
            type=self.workflow_collection_image_type,
            image=settings.MEDIA_ROOT + "/wumbo.jpg",
            collection=self.workflow_collection,
        )
        self.workflow_collection_image_2 = WorkflowCollectionImageFactory(
            type=self.workflow_collection_image_type_2,
            image=settings.MEDIA_ROOT + "/wumbo2.jpg",
            collection=self.workflow_collection,
        )
        self.image_1_dict = {
            "image_url": f"http://testserver{self.workflow_collection_image.image.url}",
            "image_type": self.workflow_collection_image.type.type,
        }
        self.image_2_dict = {
            "image_url": f"http://testserver{self.workflow_collection_image_2.image.url}",
            "image_type": self.workflow_collection_image_2.type.type,
        }

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
                "assignment_only",
                "recommendable",
                "name",
                "ordered",
                "workflowcollectionmember_set",
                "authors",
                "images",
                "category",
                "metadata",
                "newer_version",
                "dependencies_completed",
            ],
        )

        self.assertEqual(response.data["code"], self.workflow_collection.code)
        self.assertEqual(response.data["name"], self.workflow_collection.name)
        self.assertEqual(response.data["ordered"], self.workflow_collection.ordered)
        self.assertEqual(response.data["category"], self.workflow_collection.category)
        self.assertEqual(
            response.data["workflowcollectionmember_set"][0]["workflow"]["detail"],
            "http://testserver/api/workflow_system/workflows/{}/".format(
                self.workflow.id
            ),
        )
        self.assertEqual(
            response.data["workflowcollectionmember_set"][0]["order"],
            self.workflow_collection_member.order,
        )
        self.assertEqual(
            response.data["authors"][0]["user"]["first_name"],
            self.workflow.author.user.first_name,
        )
        self.assertEqual(
            response.data["authors"][0]["user"]["last_name"],
            self.workflow.author.user.last_name,
        )
        self.assertEqual(response.data["metadata"][0][0], "Eggs")
        self.assertEqual(
            response.data["images"], [self.image_1_dict, self.image_2_dict]
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
            "/workflows/collections/{}/".format(
                self.simple_survey__survey_collection.id
            ),
            data={"include_steps": "true"},
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
                "assignment_only",
                "recommendable",
                "name",
                "ordered",
                "workflowcollectionmember_set",
                "authors",
                "images",
                "category",
                "metadata",
                "newer_version",
            ],
        )
        self.assertEqual(len(response.data["workflowcollectionmember_set"]), 1)
        for workflow_collection_member in response.data["workflowcollectionmember_set"]:
            self.assertListEqual(
                list(workflow_collection_member.keys()), ["order", "workflow"]
            )
            workflow = workflow_collection_member["workflow"]
            self.assertListEqual(
                list(workflow.keys()),
                [
                    "id",
                    "detail",
                    "code",
                    "name",
                    "author",
                    "images",
                    "workflowstep_set",
                    "metadata",
                ],
            )
            workflow_step_set = workflow["workflowstep_set"]
            self.assertEqual(len(workflow_step_set), 1)
            for step in workflow_step_set:
                self.assertListEqual(
                    list(step.keys()),
                    [
                        "id",
                        "code",
                        "order",
                        "ui_template",
                        "workflowstepuserinput_set",
                        "workflowsteptext_set",
                        "workflowstepaudio_set",
                        "workflowstepimage_set",
                        "workflowstepvideo_set",
                        "workflowstepexternallink_set",
                    ],
                )

    def test_get_include_steps__fail(self):
        """Ensure response payload is as expected."""
        request = self.factory.get(
            "/workflows/collections/{}/".format(
                self.simple_survey__survey_collection.id
            ),
            data={"include_steps": "beef"},
        )
        request.user = self.user
        response = self.view(request, self.simple_survey__survey_collection.id)

        self.assertEqual(response.status_code, 400)
