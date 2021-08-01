from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from django_workflow_system.api.tests.factories import (
    WorkflowFactory,
    WorkflowStepFactory,
    UserFactory,
)
from django_workflow_system.api.tests.factories.workflows.metadata import (
    WorkflowMetadataFactory,
)
from django_workflow_system.api.tests.factories.workflows.step import (
    _WorkflowStepVideoFactory,
)
from django_workflow_system.api.tests.factories.workflows.workflow_image import (
    WorkflowImageTypeFactory,
    WorkflowImageFactory,
)
from django_workflow_system.api.views.workflows import WorkflowsView, WorkflowView
from django_workflow_system.models import WorkflowAuthor


class TestWorkflowsView(TestCase):
    """Test WorkflowsView class."""

    def setUp(self):
        self.view = WorkflowsView.as_view()
        self.factory = APIRequestFactory()
        self.workflow = WorkflowFactory()
        self.workflow_2 = WorkflowFactory()
        self.user = UserFactory()

        # IMAGES
        self.workflow_image_type = WorkflowImageTypeFactory(type="Detail")
        self.workflow_image_type_2 = WorkflowImageTypeFactory(type="Homepage")

        self.workflow_metadata_1 = WorkflowMetadataFactory(
            name="Eggs", description="Chicken Product"
        )
        self.workflow_metadata_2 = WorkflowMetadataFactory(
            name="Bacon", description="Pork Product"
        )

        self.workflow.metadata.add(self.workflow_metadata_1)
        self.workflow_2.metadata.add(self.workflow_metadata_2)

        self.workflow_image = WorkflowImageFactory(
            type=self.workflow_image_type,
            image=settings.MEDIA_ROOT + "/wumbo.jpg",
            workflow=self.workflow,
        )
        self.workflow_image_2 = WorkflowImageFactory(
            type=self.workflow_image_type_2,
            image=settings.MEDIA_ROOT + "/wumbo2.jpg",
            workflow=self.workflow,
        )
        self.workflow_image_3 = WorkflowImageFactory(
            type=self.workflow_image_type,
            image=settings.MEDIA_ROOT + "/wumbo3.jpg",
            workflow=self.workflow_2,
        )

        self.image_1_dict = {
            "image_url": f"http://testserver{self.workflow_image.image.url}",
            "image_type": self.workflow_image.type.type,
        }
        self.image_2_dict = {
            "image_url": f"http://testserver{self.workflow_image_2.image.url}",
            "image_type": self.workflow_image_2.type.type,
        }
        self.image_3_dict = {
            "image_url": f"http://testserver{self.workflow_image_3.image.url}",
            "image_type": self.workflow_image_3.type.type,
        }

    def test_get__success(self):
        """Ensure expected Workflow data is returned."""
        request = self.factory.get("/workflows/workflows/")
        request.user = self.user
        response = self.view(request)

        self.assertEqual(response.status_code, 200)

        # Correct number of workflows are returned
        self.assertEqual(len(response.data), 2)
        for result in response.data:
            # Ensure all expected data parameters are present.
            self.assertListEqual(
                list(result.keys()),
                ["id", "name", "detail", "images", "author", "metadata"],
            )

            author_obj = WorkflowAuthor.objects.get(id=result["author"]["id"])
            print(result["images"])
            # Validate the content of each returned Workflow
            if result["name"] == self.workflow.name:
                self.assertEqual(result["author"]["title"], author_obj.title)
                self.assertEqual(
                    result["author"]["user"]["first_name"], author_obj.user.first_name
                )
                self.assertEqual(
                    result["author"]["user"]["last_name"], author_obj.user.last_name
                )
                self.assertCountEqual(
                    result["images"], [self.image_1_dict, self.image_2_dict]
                )
                self.assertEqual(result["metadata"][0][0], "Eggs")

            elif result["name"] == self.workflow_2.name:
                self.assertEqual(result["author"]["title"], author_obj.title)
                self.assertEqual(
                    result["author"]["user"]["first_name"], author_obj.user.first_name
                )
                self.assertEqual(
                    result["author"]["user"]["last_name"], author_obj.user.last_name
                )
                self.assertCountEqual(result["images"], [self.image_3_dict])
                self.assertEqual(result["metadata"][0][0], "Bacon")


class TestWorkflowView(TestCase):
    """Test WorkflowView class."""

    #
    def setUp(self):
        self.view = WorkflowView.as_view()
        self.factory = APIRequestFactory()

        self.user = UserFactory()
        self.workflow = WorkflowFactory()
        self.workflow_step = WorkflowStepFactory(workflow=self.workflow)
        self.workflow_step_video = _WorkflowStepVideoFactory(
            workflow_step=self.workflow_step
        )

        self.workflow_metadata_1 = WorkflowMetadataFactory(
            name="Eggs", description="Chicken Product"
        )
        self.workflow.metadata.add(self.workflow_metadata_1)

        # IMAGES
        self.workflow_image_type = WorkflowImageTypeFactory(type="Detail")
        self.workflow_image_type_2 = WorkflowImageTypeFactory(type="Homepage")
        self.workflow_image = WorkflowImageFactory(
            type=self.workflow_image_type,
            image=settings.MEDIA_ROOT + "/wumbo.jpg",
            workflow=self.workflow,
        )
        self.workflow_image_2 = WorkflowImageFactory(
            type=self.workflow_image_type_2,
            image=settings.MEDIA_ROOT + "/wumbo2.jpg",
            workflow=self.workflow,
        )

        self.image_1_dict = {
            "image_url": f"http://testserver{self.workflow_image.image.url}",
            "image_type": self.workflow_image.type.type,
        }
        self.image_2_dict = {
            "image_url": f"http://testserver{self.workflow_image_2.image.url}",
            "image_type": self.workflow_image_2.type.type,
        }

    def test_get__success(self):
        """Ensure returned data is as expected."""
        request = self.factory.get(f"/workflows/workflows/{self.workflow.id}/")
        request.user = self.user
        response = self.view(request, self.workflow.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["code"], self.workflow.code)
        self.assertEqual(response.data["name"], self.workflow.name)
        self.assertEqual(response.data["author"]["title"], self.workflow.author.title)
        self.assertEqual(response.data["metadata"][0][0], "Eggs")
        self.assertEqual(
            response.data["author"]["image"],
            f"http://testserver/mediafiles/{str(self.workflow.author.image)}",
        )
        self.assertEqual(
            response.data["author"]["user"]["first_name"],
            self.workflow.author.user.first_name,
        )
        self.assertEqual(
            response.data["author"]["user"]["last_name"],
            self.workflow.author.user.last_name,
        )
        self.assertEqual(
            response.data["workflowstep_set"][0]["workflowstepvideo_set"][0][
                "ui_identifier"
            ],
            self.workflow_step_video.ui_identifier,
        )
        self.assertEqual(
            response.data["workflowstep_set"][0]["code"], self.workflow_step.code
        )
        self.assertCountEqual(
            response.data["images"], [self.image_1_dict, self.image_2_dict]
        )

    def test_get__workflow_id_nonexistent(self):
        """using non-existing workflow ID"""
        made_up_uuiid = "4f84f799-9cc5-43d3-0000-24840b7eb8ce"
        request = self.factory.get(f"/workflows/workflows/{made_up_uuiid}/")
        request.user = self.user
        response = self.view(request, made_up_uuiid)

        self.assertEqual(response.status_code, 404)
