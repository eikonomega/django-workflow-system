from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from rest_framework.test import APIRequestFactory

from django_workflow_system.api.tests.factories import (
    UserFactory,
    WorkflowCollectionFactory,
)
from django_workflow_system.api.tests.factories.workflows import (
    JSONSchemaTrueFactory,
    JSONSchemaFactory,
    WorkflowCollectionEngagementFactory,
    WorkflowCollectionEngagementDetailFactory,
)
from django_workflow_system.api.tests.factories.workflows.step import (
    _WorkflowStepUserInputTypeFactory,
)
from django_workflow_system.api.views.user.workflows import (
    WorkflowCollectionEngagementsView,
    WorkflowCollectionEngagementDetailsView,
    WorkflowCollectionEngagementView,
)
from django_workflow_system.models import (
    Workflow,
    WorkflowStep,
    WorkflowStepUserInput,
    WorkflowCollectionEngagementDetail,
)


class TestWorkflowCollectionSurveys(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = UserFactory()
        self.maxDiff = 1000
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
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},
                                    }
                                ],
                            },
                            {
                                "code": "step2",
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},
                                    }
                                ],
                            },
                            {
                                "code": "step3",
                                "workflowsteptext_set": [{"text": "Thank u"}],
                            },
                        ],
                    }
                ],
            }
        )
        self.diamond_scenario__survey_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "name": "pet_survey_collection",
                "workflow_set": [
                    {
                        "name": "pet_quiz_workflow",
                        "code": "pet_quiz_workflow",
                        "workflowstep_set": [
                            {
                                "code": "cat_or_dog",
                                "workflowsteptext_set": [
                                    {"text": "cats"},
                                    {"text": "dogs"},
                                ],
                                "workflowstepuserinput_set": [
                                    {
                                        "ui_identifier": "question_1",
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},
                                    }
                                ],
                            },
                            {
                                "code": "fav_cat",
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},  # accept anything
                                    }
                                ],
                            },
                            {
                                "code": "fav_dog",
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},  # accept anything
                                    }
                                ],
                            },
                            {
                                "code": "final_step",
                                "workflowsteptext_set": [
                                    {"text": "Thank you for completing the survey!"}
                                ],
                            },
                        ],
                    }
                ],
                "workflowstepdependencygroup_set": [
                    {
                        "workflow_step": {
                            "workflow__code": "pet_quiz_workflow",
                            "code": "fav_cat",
                        },
                        "workflowstepdependencydetail_set": [
                            {
                                "dependency_step": {"code": "cat_or_dog"},
                                "required_response": {
                                    "$schema": "http://json-schema.org/draft-07/schema#",
                                    "type": "array",
                                    "items": [
                                        {
                                            "type": "object",
                                            "required": [
                                                "stepInputID",
                                                "stepInputUIIdentifier",
                                                "userInput",
                                            ],
                                            "properties": {
                                                "stepInputID": {"type": "string"},
                                                "stepInputUIIdentifier": {
                                                    "type": "string",
                                                    "const": "question_1",
                                                },
                                                "userInput": {
                                                    "type": "number",
                                                    "const": 0,
                                                },
                                            },
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                    {
                        "workflow_step": {
                            "workflow__code": "pet_quiz_workflow",
                            "code": "fav_dog",
                        },
                        "workflowstepdependencydetail_set": [
                            {
                                "dependency_step": {"code": "cat_or_dog"},
                                "required_response": {
                                    "$schema": "http://json-schema.org/draft-07/schema#",
                                    "type": "array",
                                    "items": [
                                        {
                                            "type": "object",
                                            "required": [
                                                "stepInputID",
                                                "stepInputUIIdentifier",
                                                "userInput",
                                            ],
                                            "properties": {
                                                "stepInputID": {"type": "string"},
                                                "stepInputUIIdentifier": {
                                                    "type": "string",
                                                    "const": "question_1",
                                                },
                                                "userInput": {
                                                    "type": "number",
                                                    "const": 1,
                                                },
                                            },
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                ],
            }
        )
        self.multiple_dependency_groups__survey_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "name": "pet_survey_collection_with_bees",
                "workflow_set": [
                    {
                        "name": "pet_quiz_workflow_with_bees",
                        "code": "pet_quiz_workflow_with_bees",
                        "workflowstep_set": [
                            {
                                "code": "cat_or_dog_or_bees",
                                "workflowsteptext_set": [
                                    {"text": "cats"},
                                    {"text": "dogs"},
                                    {"text": "bees"},
                                ],
                                "workflowstepuserinput_set": [
                                    {
                                        "ui_identifier": "question_1",
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(
                                            json_schema={
                                                "properties": {
                                                    "correctAnswer": {
                                                        "type": "number",
                                                        "enum": [0, 1, 2],
                                                    },
                                                    "options": {
                                                        "type": "array",
                                                        "items": {
                                                            "anyOf": [
                                                                {"type": "number"},
                                                                {"type": "string"},
                                                            ]
                                                        },
                                                    },
                                                }
                                            }
                                        ),
                                        "specification": {
                                            "options": [0, 1, 2],
                                            "correctAnswer": 0,
                                        },
                                    }
                                ],
                            },
                            {
                                "code": "good_choice",
                                "workflowsteptext_set": [
                                    {
                                        "text": "good choice!",
                                    }
                                ],
                            },
                            {
                                "code": "final_step",
                                "workflowsteptext_set": [
                                    {"text": "Thank you for completing the survey!"}
                                ],
                            },
                        ],
                    }
                ],
                "workflowstepdependencygroup_set": [
                    {
                        "workflow_step": {
                            "workflow__code": "pet_quiz_workflow_with_bees",
                            "code": "good_choice",
                        },
                        "workflowstepdependencydetail_set": [
                            {
                                "dependency_step": {"code": "cat_or_dog_or_bees"},
                                "required_response": {
                                    "$schema": "http://json-schema.org/draft-07/schema#",
                                    "type": "array",
                                    "items": [
                                        {
                                            "type": "object",
                                            "required": [
                                                "stepInputID",
                                                "stepInputUIIdentifier",
                                                "userInput",
                                            ],
                                            "properties": {
                                                "stepInputID": {"type": "string"},
                                                "stepInputUIIdentifier": {
                                                    "type": "string",
                                                    "const": "question_1",
                                                },
                                                "userInput": {
                                                    "type": "number",
                                                    "const": 0,
                                                },
                                            },
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                    {
                        "workflow_step": {
                            "workflow__code": "pet_quiz_workflow_with_bees",
                            "code": "good_choice",
                        },
                        "workflowstepdependencydetail_set": [
                            {
                                "dependency_step": {"code": "cat_or_dog_or_bees"},
                                "required_response": {
                                    "$schema": "http://json-schema.org/draft-07/schema#",
                                    "type": "array",
                                    "items": [
                                        {
                                            "type": "object",
                                            "required": [
                                                "stepInputID",
                                                "stepInputUIIdentifier",
                                                "userInput",
                                            ],
                                            "properties": {
                                                "stepInputID": {"type": "string"},
                                                "stepInputUIIdentifier": {
                                                    "type": "string",
                                                    "const": "question_1",
                                                },
                                                "userInput": {
                                                    "type": "number",
                                                    "const": 1,
                                                },
                                            },
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                ],
            }
        )

    def test_survey_integration_simple(self):
        """
        Simple survey integration test:
        1 -> 2 -> 3
        """
        collection = self.simple_survey__survey_collection
        workflow = Workflow.objects.get(name="simple_survey_workflow")
        steps = list(WorkflowStep.objects.filter(workflow=workflow).order_by("order"))

        """Valid JSON payloads return 201."""
        request = self.factory.post(
            "/users/self/workflows/engagements/",
            data={
                "workflow_collection": f"http://testserver/api/workflow_system/collections/{collection.id}/"
            },
            format="json",
        )

        request.user = self.user
        response = WorkflowCollectionEngagementsView.as_view()(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(
            response.data["workflow_collection"],
            f"http://testserver/api/workflow_system/collections/{collection.id}/",
        )
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "next_step_id": steps[0].id,
                "prev_workflow": None,
                "prev_step_id": None,
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 0,
                "steps_completed_in_workflow": 0,
                "steps_in_collection": 3,
                "steps_in_workflow": 3,
            },
        )

        """
        get user engagement id from this string in response.data['detail']
        http://testserver/api_v3/users/self/workflows/engagements/62eb8dd9-f961-4448-8408-50e3a6e5b80b/
        """
        workflow_user_engagement_id = str(response.data["self_detail"]).split("/")[-2]
        # get step info... the wrong way
        step_input = WorkflowStepUserInput.objects.get(workflow_step=steps[0])
        ################
        request = self.factory.post(
            f"/users/self/workflows/engagements/{workflow_user_engagement_id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{workflow_user_engagement_id}/",
                "step": steps[0].id,
                "started": timezone.now(),
                "finished": timezone.now() + timezone.timedelta(milliseconds=1),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(step_input.id),
                                "stepInputUIIdentifier": str(step_input.ui_identifier),
                                "userInput": "Stegosaurus",
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, workflow_user_engagement_id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "next_step_id": steps[1].id,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "prev_step_id": steps[0].id,
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 1,
                "steps_completed_in_workflow": 1,
                "steps_in_collection": 3,
                "steps_in_workflow": 3,
            },
        )

        # get step info... the wrong way
        step_input = WorkflowStepUserInput.objects.get(workflow_step=steps[1])
        request = self.factory.post(
            f"/users/self/workflows/engagements/{workflow_user_engagement_id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{workflow_user_engagement_id}/",
                "step": steps[1].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=2),
                "finished": timezone.now() + timezone.timedelta(milliseconds=3),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(step_input.id),
                                "stepInputUIIdentifier": str(step_input.ui_identifier),
                                "userInput": "Orange",
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, workflow_user_engagement_id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": "http://testserver/api/workflow_system/workflows/{}/".format(
                    workflow.id
                ),
                "next_step_id": steps[2].id,
                "prev_workflow": "http://testserver/api/workflow_system/workflows/{}/".format(
                    workflow.id
                ),
                "prev_step_id": steps[1].id,
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 2,
                "steps_completed_in_workflow": 2,
                "steps_in_collection": 3,
                "steps_in_workflow": 3,
            },
        )

        request = self.factory.post(
            f"/users/self/workflows/engagements/{workflow_user_engagement_id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/"
                f"{workflow_user_engagement_id}/",
                "step": steps[2].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=4),
                "finished": timezone.now() + timezone.timedelta(milliseconds=5)
                # no user response this time
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, workflow_user_engagement_id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": None,
                "next_step_id": None,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "prev_step_id": steps[2].id,
                "previously_completed_workflows": [
                    {
                        "workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/"
                    }
                ],
                "steps_completed_in_collection": 3,
                "steps_completed_in_workflow": 3,
                "steps_in_collection": 3,
                "steps_in_workflow": 3,
            },
        )

    def test_diamond_scenario(self):
        """
        diamond scenario:
        1 --> 2
        |     |
        V     V
        3 --> 4

        1. do you like cats or dogs? cats-> 2, dogs->3
        2. what is your favorite cat?
        3. What is your favorite dog?
        4. Good job!
        """
        collection = self.diamond_scenario__survey_collection
        workflow = Workflow.objects.get(name="pet_quiz_workflow")
        steps = workflow.workflowstep_set.order_by("order")
        steps = list(steps)  # don't be lazy!

        """Valid JSON payloads return 201."""
        request = self.factory.post(
            "/users/self/workflows/engagements/",
            data={
                "workflow_collection": f"http://testserver/api/workflow_system/collections/{collection.id}/"
            },
            format="json",
        )

        request.user = self.user
        response = WorkflowCollectionEngagementsView.as_view()(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(
            response.data["workflow_collection"],
            f"http://testserver/api/workflow_system/collections/{collection.id}/",
        )
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "next_step_id": steps[0].id,
                "prev_workflow": None,
                "prev_step_id": None,
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 0,
                "steps_completed_in_workflow": 0,
                "steps_in_collection": 4,
                "steps_in_workflow": 4,
            },
        )

        """
        get user engagement id from this string in response.data['detail']
        http://testserver/api_v3/users/self/workflows/engagements/62eb8dd9-f961-4448-8408-50e3a6e5b80b/
        """
        workflow_user_engagement_id = str(response.data["self_detail"]).split("/")[-2]
        # get step info... a less wrong way
        step_input = steps[0].workflowstepuserinput_set.get()

        request = self.factory.post(
            f"/users/self/workflows/engagements/{workflow_user_engagement_id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{workflow_user_engagement_id}/",
                "step": steps[0].id,
                "started": timezone.now(),
                "finished": timezone.now() + timezone.timedelta(milliseconds=1),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(step_input.id),
                                "stepInputUIIdentifier": str(step_input.ui_identifier),
                                "userInput": 1,  # we like dogs
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, workflow_user_engagement_id
        )

        detail = list(WorkflowCollectionEngagementDetail.objects.all())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_step_id": steps[2].id,
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "prev_step_id": steps[0].id,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 2,
                "steps_completed_in_workflow": 2,
                "steps_in_collection": 4,
                "steps_in_workflow": 4,
            },
        )

        # get step info... the wrong way
        step_input_2 = WorkflowStepUserInput.objects.get(workflow_step=steps[2])
        request = self.factory.post(
            "/users/self/workflows/engagements/{}/details/".format(
                workflow_user_engagement_id
            ),
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{workflow_user_engagement_id}/",
                "step": steps[2].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=2),
                "finished": timezone.now() + timezone.timedelta(milliseconds=3),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(step_input_2.id),
                                "stepInputUIIdentifier": str(
                                    step_input_2.ui_identifier
                                ),
                                "userInput": "Corgie",
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, workflow_user_engagement_id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "next_step_id": steps[3].id,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "prev_step_id": steps[2].id,
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 3,
                "steps_completed_in_workflow": 3,
                "steps_in_collection": 4,
                "steps_in_workflow": 4,
            },
        )

        request = self.factory.post(
            "/users/self/workflows/engagements/{}/details/".format(
                workflow_user_engagement_id
            ),
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{workflow_user_engagement_id}/",
                "step": steps[3].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=4),
                "finished": timezone.now() + timezone.timedelta(milliseconds=5)
                # no user response this time
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, workflow_user_engagement_id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": None,
                "next_step_id": None,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "prev_step_id": steps[3].id,
                "previously_completed_workflows": [
                    {
                        "workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/"
                    },
                ],
                "steps_completed_in_collection": 4,
                "steps_completed_in_workflow": 4,
                "steps_in_collection": 4,
                "steps_in_workflow": 4,
            },
        )

    def test_next_step_different_workflow(self):
        collection_factory_spec = {
            "name": "two_workflow_survey",
            "category": "SURVEY",
            "workflow_set": [
                {
                    "name": "workflow_1",
                    "workflowstep_set": [
                        {
                            "code": "step1",
                            "workflowstepuserinput_set": [
                                {
                                    "ui_identifier": "question_1",
                                    "type": _WorkflowStepUserInputTypeFactory(),
                                    "specification": {},
                                }
                            ],
                        }
                    ],
                },
                {
                    "name": "workflow_2",
                    "workflowstep_set": [
                        {
                            "code": "step1",
                            "workflowsteptext_set": [{"text": "in tarnation?"}],
                        }
                    ],
                },
            ],
        }

        collection = WorkflowCollectionFactory(**collection_factory_spec)
        workflow1 = Workflow.objects.get(name="workflow_1")
        workflow2 = Workflow.objects.get(name="workflow_2")
        steps = list(workflow1.workflowstep_set.order_by("order")) + list(
            workflow2.workflowstep_set.order_by("order")
        )

        """Valid JSON payloads return 201."""
        request = self.factory.post(
            "/users/self/workflows/engagements/",
            data={
                "workflow_collection": f"http://testserver/api/workflow_system/collections/{collection.id}/"
            },
            format="json",
        )

        request.user = self.user
        response = WorkflowCollectionEngagementsView.as_view()(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 6)
        self.assertEqual(
            response.data["workflow_collection"],
            f"http://testserver/api/workflow_system/collections/{collection.id}/",
        )
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow1.id}/",
                "next_step_id": steps[0].id,
                "prev_workflow": None,
                "prev_step_id": None,
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 0,
                "steps_completed_in_workflow": 0,
                "steps_in_collection": 2,
                "steps_in_workflow": 1,
            },
        )

        # get user engagement id from this string in response.data['detail']
        # http://testserver/api_v3/users/self/workflows/engagements/62eb8dd9-f961-4448-8408-50e3a6e5b80b/
        workflow_user_engagement_id = str(response.data["self_detail"]).split("/")[-2]
        # get step info... the wrong way
        step_input = WorkflowStepUserInput.objects.get(workflow_step=steps[0])

        request = self.factory.post(
            f"/users/self/workflows/engagements/{workflow_user_engagement_id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{workflow_user_engagement_id}/",
                "step": steps[0].id,
                "started": timezone.now(),
                "finished": timezone.now() + timezone.timedelta(milliseconds=1),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(step_input.id),
                                "stepInputUIIdentifier": str(step_input.ui_identifier),
                                "userInput": "wut",
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, workflow_user_engagement_id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow2.id}/",
                "next_step_id": steps[1].id,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow1.id}/",
                "prev_step_id": steps[0].id,
                "previously_completed_workflows": [
                    {
                        "workflow": f"http://testserver/api/workflow_system/workflows/{workflow1.id}/"
                    }
                ],
                "steps_completed_in_collection": 1,
                "steps_completed_in_workflow": 0,
                "steps_in_collection": 2,
                "steps_in_workflow": 1,
            },
        )
        ################
        request = self.factory.post(
            "/users/self/workflows/engagements/{workflow_user_engagement_id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{workflow_user_engagement_id}/",
                "step": steps[1].id,
                "started": timezone.now(),
                "finished": timezone.now() + timezone.timedelta(milliseconds=1)
                # No user response
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, workflow_user_engagement_id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": None,
                "next_step_id": None,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow2.id}/",
                "prev_step_id": steps[1].id,
                "previously_completed_workflows": [
                    {
                        "workflow": f"http://testserver/api/workflow_system/workflows/{workflow1.id}/"
                    },
                    {
                        "workflow": f"http://testserver/api/workflow_system/workflows/{workflow2.id}/"
                    },
                ],
                "steps_completed_in_collection": 2,
                "steps_completed_in_workflow": 1,
                "steps_in_collection": 2,
                "steps_in_workflow": 1,
            },
        )

    def test_multiple_workflow_step_dependency_groups_cat(self):
        # cat lover gets the special message
        collection = self.multiple_dependency_groups__survey_collection
        workflow = Workflow.objects.get(code="pet_quiz_workflow_with_bees")
        steps = workflow.workflowstep_set.order_by("order")

        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=self.user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                "step": steps[0].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=1),
                "finished": timezone.now() + timezone.timedelta(milliseconds=2),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(
                                    steps[0].workflowstepuserinput_set.get().id
                                ),
                                "stepInputUIIdentifier": str(
                                    steps[0]
                                    .workflowstepuserinput_set.get()
                                    .ui_identifier
                                ),
                                "userInput": 0,
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, engagement.id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_step_id": steps[1].id,
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "prev_step_id": steps[0].id,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 1,
                "steps_completed_in_workflow": 1,
                "steps_in_collection": 3,
                "steps_in_workflow": 3,
            },
        )

    def test_multiple_workflow_step_dependency_groups_dog(self):
        # dog lover gets the special message
        collection = self.multiple_dependency_groups__survey_collection
        workflow = Workflow.objects.get(code="pet_quiz_workflow_with_bees")
        steps = workflow.workflowstep_set.order_by("order")

        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=self.user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                "step": steps[0].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=1),
                "finished": timezone.now() + timezone.timedelta(milliseconds=2),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(
                                    steps[0].workflowstepuserinput_set.get().id
                                ),
                                "stepInputUIIdentifier": str(
                                    steps[0]
                                    .workflowstepuserinput_set.get()
                                    .ui_identifier
                                ),
                                "userInput": 1,
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, engagement.id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_step_id": steps[1].id,
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "prev_step_id": steps[0].id,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 1,
                "steps_completed_in_workflow": 1,
                "steps_in_collection": 3,
                "steps_in_workflow": 3,
            },
        )

    def test_multiple_workflow_step_dependency_groups_bees(self):
        # bee lover does not get the special message
        collection = self.multiple_dependency_groups__survey_collection
        workflow = Workflow.objects.get(code="pet_quiz_workflow_with_bees")
        steps = workflow.workflowstep_set.order_by("order")

        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=self.user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                "step": steps[0].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=1),
                "finished": timezone.now() + timezone.timedelta(milliseconds=2),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(
                                    steps[0].workflowstepuserinput_set.get().id
                                ),
                                "stepInputUIIdentifier": str(
                                    steps[0]
                                    .workflowstepuserinput_set.get()
                                    .ui_identifier
                                ),
                                "userInput": 2,
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, engagement.id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "next_step_id": steps[2].id,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "prev_step_id": steps[0].id,
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 2,
                "steps_completed_in_workflow": 2,
                "steps_in_collection": 3,
                "steps_in_workflow": 3,
            },
        )

    def test_no_stepInputID_400(self):
        # a survey response with no stepInputId should 400
        collection = self.simple_survey__survey_collection
        workflow = Workflow.objects.get(code="simple_survey_workflow")
        steps = workflow.workflowstep_set.order_by("order")

        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=self.user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                "step": steps[0].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=1),
                "finished": timezone.now() + timezone.timedelta(milliseconds=2),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                # "stepInputID": str(steps[0].workflowstepuserinput_set.get().id),
                                "stepInputUIIdentifier": str(
                                    steps[0]
                                    .workflowstepuserinput_set.get()
                                    .ui_identifier
                                ),
                                "userInput": 0,
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, engagement.id
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_stepInputUIIdentifier_400s(self):
        # a survey response with no stepInputUIIdentifier should 400
        collection = self.simple_survey__survey_collection
        workflow = Workflow.objects.get(code="simple_survey_workflow")
        steps = workflow.workflowstep_set.order_by("order")

        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=self.user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                "step": steps[0].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=1),
                "finished": timezone.now() + timezone.timedelta(milliseconds=2),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(
                                    steps[0].workflowstepuserinput_set.get().id
                                ),
                                # "stepInputUIIdentifier": str(
                                #     steps[0].workflowstepuserinput_set.get().ui_identifier),
                                "userInput": 0,
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, engagement.id
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_step_id(self):
        # a survey response with an invalid step id should 400
        collection = self.simple_survey__survey_collection
        workflow = Workflow.objects.get(code="simple_survey_workflow")
        steps = workflow.workflowstep_set.order_by("order")

        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=self.user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/users/self/workflows/engagements/{engagement.id}/",
                "step": steps[0].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=1),
                "finished": timezone.now() + timezone.timedelta(milliseconds=2),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": "hotdog",
                                "stepInputUIIdentifier": str(
                                    steps[0]
                                    .workflowstepuserinput_set.get()
                                    .ui_identifier
                                ),
                                "userInput": 0,
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, engagement.id
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ui_identifer_matches_step_input_id(self):
        # a survey response where step with the provided id has a different ui identifier should 400
        collection = self.simple_survey__survey_collection
        workflow = Workflow.objects.get(code="simple_survey_workflow")
        steps = workflow.workflowstep_set.order_by("order")

        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=self.user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                "step": steps[0].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=1),
                "finished": timezone.now() + timezone.timedelta(milliseconds=2),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(
                                    steps[0].workflowstepuserinput_set.get().id
                                ),
                                "stepInputUIIdentifier": "burger",
                                "userInput": 0,
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, engagement.id
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfinished_step_counts_as_requirement_not_fulfilled(self):
        """"""
        collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "name": "rice_survey_collection",
                "workflow_set": [
                    {
                        "name": "rice_survey_workflow",
                        "code": "rice_survey_workflow",
                        "workflowstep_set": [
                            {
                                "code": "have_rice",
                                "workflowsteptext_set": [
                                    {"text": "yes"},
                                    {"text": "no"},
                                ],
                                "workflowstepuserinput_set": [
                                    {
                                        "ui_identifier": "question_1",
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},
                                    }
                                ],
                            },
                            {
                                "code": "red_rice",
                                "workflowsteptext_set": [
                                    {"text": "yes"},
                                    {"text": "no"},
                                ],
                                "workflowstepuserinput_set": [
                                    {
                                        "ui_identifier": "question_1",
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},
                                    }
                                ],
                            },
                            {
                                "code": "nice_rice",
                                "workflowsteptext_set": [{"text": "I like red rice!"}],
                            },
                            {
                                "code": "final_step",
                                "workflowsteptext_set": [
                                    {"text": "Thank you for completing the survey!"}
                                ],
                            },
                        ],
                    }
                ],
                "workflowstepdependencygroup_set": [
                    {
                        "workflow_step": {
                            "workflow__code": "rice_survey_workflow",
                            "code": "red_rice",
                        },
                        "workflowstepdependencydetail_set": [
                            {
                                "dependency_step": {"code": "have_rice"},
                                "required_response": {
                                    "$schema": "http://json-schema.org/draft-07/schema#",
                                    "type": "array",
                                    "items": [
                                        {
                                            "type": "object",
                                            "required": [
                                                "stepInputID",
                                                "stepInputUIIdentifier",
                                                "response",
                                            ],
                                            "properties": {
                                                "stepInputID": {"type": "string"},
                                                "stepInputUIIdentifier": {
                                                    "type": "string",
                                                    "const": "question_1",
                                                },
                                                "response": {
                                                    "type": "number",
                                                    "const": 1,
                                                },
                                            },
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                    {
                        "workflow_step": {
                            "workflow__code": "rice_survey_workflow",
                            "code": "nice_rice",
                        },
                        "workflowstepdependencydetail_set": [
                            {
                                "dependency_step": {"code": "red_rice"},
                                "required_response": {
                                    "$schema": "http://json-schema.org/draft-07/schema#",
                                    "type": "array",
                                    "items": [
                                        {
                                            "type": "object",
                                            "required": [
                                                "stepInputID",
                                                "stepInputUIIdentifier",
                                                "response",
                                            ],
                                            "properties": {
                                                "stepInputID": {"type": "string"},
                                                "stepInputUIIdentifier": {
                                                    "type": "string",
                                                    "const": "question_1",
                                                },
                                                "response": {
                                                    "type": "number",
                                                    "const": 1,
                                                },
                                            },
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                ],
            }
        )

        workflow = Workflow.objects.get(code="rice_survey_workflow")
        steps = workflow.workflowstep_set.order_by("order")

        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=self.user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                "workflow_collection_engagement": f"http://testserver/api/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                "step": steps[0].id,
                "started": timezone.now() + timezone.timedelta(milliseconds=1),
                "finished": timezone.now() + timezone.timedelta(milliseconds=2),
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(
                                    steps[0].workflowstepuserinput_set.get().id
                                ),
                                "stepInputUIIdentifier": "question_1",
                                "userInput": 0,
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementDetailsView.as_view()(
            request, engagement.id
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["state"],
            {
                "next_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "next_step_id": steps[3].id,
                "prev_workflow": f"http://testserver/api/workflow_system/workflows/{workflow.id}/",
                "prev_step_id": steps[0].id,
                "previously_completed_workflows": [],
                "steps_completed_in_collection": 3,
                "steps_completed_in_workflow": 3,
                "steps_in_collection": 4,
                "steps_in_workflow": 4,
            },
        )

    def test_submit_deletes_unfinished(self):
        collection = self.diamond_scenario__survey_collection
        workflow = Workflow.objects.get(name="pet_quiz_workflow")
        steps = workflow.workflowstep_set.order_by("order")
        steps = list(steps)  # don't be lazy!

        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=self.user,
        )

        detail0 = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=engagement,
            step=steps[0],
            user_responses=0,
            started=timezone.now(),
            finished=timezone.now(),
        )
        detail1 = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=engagement,
            step=steps[1],
            user_responses="Garfield",
            started=timezone.now(),
            finished=timezone.now(),
        )
        detail2 = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=engagement,
            step=steps[2],
            user_responses="Corgi",
            started=timezone.now(),
            finished=None,
        )
        detail3 = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=engagement,
            step=steps[3],
            started=timezone.now(),
            finished=timezone.now(),
        )

        request = self.factory.patch(
            "/users/self/workflows/engagements/{}".format(engagement.id),
            data={
                "finished": timezone.now(),
            },
            format="json",
        )
        request.user = self.user
        response = WorkflowCollectionEngagementView.as_view()(request, engagement.id)

        self.assertListEqual(
            list(
                WorkflowCollectionEngagementDetail.objects.filter(
                    workflow_collection_engagement=engagement
                )
            ),
            list(
                WorkflowCollectionEngagementDetail.objects.filter(
                    workflow_collection_engagement=engagement, finished__isnull=False
                )
            ),
        )
