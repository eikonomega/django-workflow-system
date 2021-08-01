"""Unit tests."""
import dateutil
from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from rest_framework.test import APIRequestFactory

from django_workflow_system.api.tests.factories import (
    WorkflowCollectionFactory,
    UserFactory,
    WorkflowCollectionEngagementFactory,
    WorkflowCollectionEngagementDetailFactory,
)
from django_workflow_system.api.tests.factories.workflows import json_schema
from django_workflow_system.api.tests.factories.workflows.step import (
    _WorkflowStepUserInputTypeFactory,
)
from django_workflow_system.api.views.user.workflows import (
    WorkflowCollectionEngagementDetailsView,
    WorkflowCollectionEngagementDetailView,
)
from django_workflow_system.models import (
    WorkflowCollection,
    WorkflowStep,
    WorkflowStepUserInput,
)


class TestWorkflowEngagementDetailsView(TestCase):
    def setUp(self):
        self.view = WorkflowCollectionEngagementDetailsView.as_view()
        self.factory = APIRequestFactory()

        self.single_activity_collection: WorkflowCollection = WorkflowCollectionFactory(
            **{
                "category": "ACTIVITY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {"workflowsteptext_set": [{"text": "You did it"}]}
                        ]
                    }
                ],
            }
        )

        self.single_activity_collection__workflow = (
            self.single_activity_collection.workflowcollectionmember_set.get().workflow
        )
        self.single_activity_collection__step = (
            self.single_activity_collection__workflow.workflowstep_set.get()
        )

        self.single_survey_collection: WorkflowCollection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        )
        self.single_survey_collection__workflow = (
            self.single_survey_collection.workflowcollectionmember_set.get().workflow
        )
        self.single_survey_collection__step = (
            self.single_survey_collection__workflow.workflowstep_set.get()
        )
        self.single_survey_collection__input = (
            self.single_survey_collection__step.workflowstepuserinput_set.get()
        )

        self.user_with_activity_engagement = UserFactory()
        self.user_with_activity_engagement__engagement = (
            WorkflowCollectionEngagementFactory(
                workflow_collection=self.single_activity_collection,
                user=self.user_with_activity_engagement,
            )
        )
        self.user_with_activity_engagement__detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=self.user_with_activity_engagement__engagement,
            step=self.single_activity_collection__step,
        )

    def test_patch__valid_payload_with_schema(self):
        """Patch current engagement to the one specified."""
        my_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(
                                            json_schema={
                                                "type": "object",
                                                "title": "User Input: Single Choice Question",
                                                "description": "A schema representing a single choice question user input.",
                                                "required": ["label", "inputOptions"],
                                                "properties": {
                                                    "id": {
                                                        "type": "string",
                                                        "title": "A string-based user input identifier.",
                                                        "description": "This value may be managed outside of the object specification and so is optional.",
                                                        "examples": [
                                                            "4125-1351-1251-asfd"
                                                        ],
                                                    },
                                                    "label": {
                                                        "type": "string",
                                                        "title": "UI Label for Input",
                                                        "description": "Label that should be displayed by user interfaces for this input.",
                                                        "examples": [
                                                            "The label to display for the input/question."
                                                        ],
                                                    },
                                                    "inputOptions": {
                                                        "$id": "#/properties/options",
                                                        "type": "array",
                                                        "title": "Question Options",
                                                        "description": "The options to be displayed to the user for this question.",
                                                        "minItems": 2,
                                                        "uniqueItems": True,
                                                        "items": {
                                                            "anyOf": [
                                                                {"type": "number"},
                                                                {"type": "string"},
                                                            ]
                                                        },
                                                    },
                                                    "correctInput": {
                                                        "description": "Indicates which answer is the correct one.",
                                                        "anyOf": [
                                                            {"type": "string"},
                                                            {"type": "number"},
                                                        ],
                                                    },
                                                    "meta": {
                                                        "type": "object",
                                                        "properties": {
                                                            "inputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not an answer should be required from the user.",
                                                            },
                                                            "correctInputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not the correct answer should be required from the user.",
                                                            },
                                                        },
                                                    },
                                                },
                                            }
                                        ),
                                        "specification": {
                                            "label": "What is your favorite color?",
                                            "inputOptions": ["Red", "Blue"],
                                            "correctInput": "Red",
                                            "meta": {
                                                "inputRequired": True,
                                                "correctInputRequired": True,
                                            },
                                        },
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        )
        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_step_input.type.name = "single_choice_question"
        my_step_input.type.save()
        my_user = UserFactory()
        my_workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=my_collection,
            user=my_user,
        )
        my_workflow_engagement_detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=my_workflow_engagement,
            step=my_step,
            started=timezone.now(),
            finished=timezone.now(),
        )

        time_stamp = timezone.now()
        request = self.factory.patch(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/{my_workflow_engagement_detail.id}/",
            data={
                "finished": time_stamp,
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(my_step_input.id),
                                "stepInputUIIdentifier": str(
                                    my_step_input.ui_identifier
                                ),
                                "userInput": "Red",
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = my_user
        response = self.view(
            request, my_workflow_engagement.id, my_workflow_engagement_detail.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(dateutil.parser.parse(response.data["finished"]), time_stamp)
        self.assertEqual(response.data["proceed"], True)

    def test_patch__valid_payload_with_schema_existing_response(self):
        """Patch current engagement to the one specified."""
        my_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(
                                            json_schema={
                                                "type": "object",
                                                "description": "A schema representing a single choice question user input.",
                                                "required": ["label", "inputOptions"],
                                                "properties": {
                                                    "id": {
                                                        "type": "string",
                                                        "title": "A string-based user input identifier.",
                                                        "description": "This value may be managed outside of the object specification and so is optional.",
                                                        "examples": [
                                                            "4125-1351-1251-asfd"
                                                        ],
                                                    },
                                                    "label": {
                                                        "type": "string",
                                                        "title": "UI Label for Input",
                                                        "description": "Label that should be displayed by user interfaces for this input.",
                                                        "examples": [
                                                            "The label to display for the input/question."
                                                        ],
                                                    },
                                                    "inputOptions": {
                                                        "$id": "#/properties/options",
                                                        "type": "array",
                                                        "title": "Question Options",
                                                        "description": "The options to be displayed to the user for this question.",
                                                        "minItems": 2,
                                                        "uniqueItems": True,
                                                        "items": {
                                                            "anyOf": [
                                                                {"type": "number"},
                                                                {"type": "string"},
                                                            ]
                                                        },
                                                    },
                                                    "correctInput": {
                                                        "description": "Indicates which answer is the correct one.",
                                                        "anyOf": [
                                                            {"type": "string"},
                                                            {"type": "number"},
                                                        ],
                                                    },
                                                    "meta": {
                                                        "type": "object",
                                                        "properties": {
                                                            "inputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not an answer should be required from the user.",
                                                            },
                                                            "correctInputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not the correct answer should be required from the user.",
                                                            },
                                                        },
                                                    },
                                                },
                                            }
                                        ),
                                        "specification": {
                                            "label": "What is your favorite number?",
                                            "inputOptions": [1, 2, 3, 4, 5],
                                            "correctInput": 1,
                                            "meta": {
                                                "inputRequired": True,
                                                "correctInputRequired": False,
                                            },
                                        },
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        )
        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_step_input.type.name = "single_choice_question"
        my_step_input.save()
        my_user = UserFactory()
        my_workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=my_collection,
            user=my_user,
        )
        my_workflow_engagement_detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=my_workflow_engagement,
            step=my_step,
            started=timezone.now(),
            finished=timezone.now(),
            user_responses=[
                {
                    "inputs": [
                        {
                            "stepInputID": str(my_step_input.id),
                            "stepInputUIIdentifier": str(my_step_input.ui_identifier),
                            "userInput": 1,
                        }
                    ]
                }
            ],
        )

        time_stamp = timezone.now()
        request = self.factory.patch(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/{my_workflow_engagement_detail.id}/",
            data={
                "finished": time_stamp,
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(my_step_input.id),
                                "stepInputUIIdentifier": str(
                                    my_step_input.ui_identifier
                                ),
                                "userInput": 1,
                            }
                        ],
                        "submittedTime": time_stamp,
                    },
                    {
                        "inputs": [
                            {
                                "stepInputID": str(my_step_input.id),
                                "stepInputUIIdentifier": str(
                                    my_step_input.ui_identifier
                                ),
                                "userInput": 2,
                            }
                        ]
                    },
                ],
            },
            format="json",
        )
        request.user = my_user
        response = self.view(
            request, my_workflow_engagement.id, my_workflow_engagement_detail.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(dateutil.parser.parse(response.data["finished"]), time_stamp)
        self.assertEqual(len(response.data["user_responses"]), 2)
        self.assertEqual(response.data["proceed"], True)

    def test_patch__schema_fails(self):
        """Patch current engagement to the one specified."""
        my_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(
                                            json_schema={
                                                "$id": "http://github.com/crcresearch/",
                                                "type": "object",
                                                "title": "User Input: Single Choice Question",
                                                "description": "A schema representing a single choice question user input.",
                                                "required": ["label", "inputOptions"],
                                                "properties": {
                                                    "id": {
                                                        "type": "string",
                                                        "title": "A string-based user input identifier.",
                                                        "description": "This value may be managed outside of the object specification and so is optional.",
                                                        "examples": [
                                                            "4125-1351-1251-asfd"
                                                        ],
                                                    },
                                                    "label": {
                                                        "type": "string",
                                                        "title": "UI Label for Input",
                                                        "description": "Label that should be displayed by user interfaces for this input.",
                                                        "examples": [
                                                            "The label to display for the input/question."
                                                        ],
                                                    },
                                                    "inputOptions": {
                                                        "$id": "#/properties/options",
                                                        "type": "array",
                                                        "title": "Question Options",
                                                        "description": "The options to be displayed to the user for this question.",
                                                        "minItems": 2,
                                                        "uniqueItems": True,
                                                        "items": {
                                                            "anyOf": [
                                                                {"type": "number"},
                                                                {"type": "string"},
                                                            ]
                                                        },
                                                    },
                                                    "correctInput": {
                                                        "description": "Indicates which answer is the correct one.",
                                                        "anyOf": [
                                                            {"type": "string"},
                                                            {"type": "number"},
                                                        ],
                                                    },
                                                    "meta": {
                                                        "type": "object",
                                                        "properties": {
                                                            "inputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not an answer should be required from the user.",
                                                            },
                                                            "correctInputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not the correct answer should be required from the user.",
                                                            },
                                                        },
                                                    },
                                                },
                                            }
                                        ),
                                        "specification": {
                                            "label": "What is your favorite color?",
                                            "inputOptions": ["Red", "Blue"],
                                            "correctInput": "Red",
                                            "meta": {
                                                "inputRequired": False,
                                                "correctInputRequired": False,
                                            },
                                        },
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        )
        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_step_input.type.name = "single_choice_question"
        my_step_input.type.save()
        my_user = UserFactory()
        my_workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=my_collection,
            user=my_user,
        )
        my_workflow_engagement_detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=my_workflow_engagement,
            step=my_step,
            started=timezone.now(),
            finished=timezone.now(),
            user_responses=[
                {
                    "inputs": [
                        {
                            "stepInputID": str(my_step_input.id),
                            "stepInputUIIdentifier": str(my_step_input.ui_identifier),
                            "userInput": "Red",
                        },
                    ]
                }
            ],
        )
        time_stamp = timezone.now()
        request = self.factory.patch(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/{my_workflow_engagement_detail.id}/",
            data={
                "finished": time_stamp,
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputID": str(my_step_input.id),
                                "stepInputUIIdentifier": str(
                                    my_step_input.ui_identifier
                                ),
                                "userInput": "Eggs",
                            }
                        ]
                    }
                ],
            },
            format="json",
        )
        request.user = my_user
        response = self.view(
            request, my_workflow_engagement.id, my_workflow_engagement_detail.id
        )

        # This no longer raises an error, the user just can't proceed to the next step
        self.assertEqual(response.data["proceed"], False)

    def test_post__answer_NOT_required_NOT_given(self):
        my_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {"workflowstepuserinput_set": [{"required": False}]}
                        ]
                    }
                ],
            }
        )

        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_user = UserFactory()
        my_workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=my_collection,
            user=my_user,
        )
        my_workflow_engagement_detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=my_workflow_engagement,
            step=my_step,
            started=timezone.now(),
            finished=timezone.now(),
        )
        time_stamp = timezone.now()

        request = self.factory.patch(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/{my_workflow_engagement_detail.id}/",
            data={
                "finished": time_stamp,
                "user_responses": [{"inputs": []}],
            },
            format="json",
        )
        request.user = my_user
        response = self.view(
            request, my_workflow_engagement, my_workflow_engagement_detail.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["proceed"], True)

    def test_patch__answer_required_not_given(self):
        my_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        )

        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_user = UserFactory()
        my_workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=my_collection,
            user=my_user,
        )
        my_workflow_engagement_detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=my_workflow_engagement,
            step=my_step,
            started=timezone.now(),
            finished=timezone.now(),
        )
        time_stamp = timezone.now()

        request = self.factory.patch(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/{my_workflow_engagement_detail.id}/",
            data={
                "finished": time_stamp,
                "user_responses": [{"inputs": []}],
            },
            format="json",
        )
        request.user = my_user
        response = self.view(
            request, my_workflow_engagement.id, my_workflow_engagement_detail.id
        )

        self.assertEqual(response.status_code, 400)

    def test_patch__inputs_not_in_user_responses(self):
        my_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(),
                                        "specification": {},
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        )

        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_user = UserFactory()
        my_workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=my_collection,
            user=my_user,
        )
        my_workflow_engagement_detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=my_workflow_engagement,
            step=my_step,
            started=timezone.now(),
            finished=timezone.now() + timezone.timedelta(1),
        )

        time_stamp = timezone.now()

        request = self.factory.patch(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/{my_workflow_engagement_detail.id}/",
            data={
                "finished": time_stamp,
                "user_responses": [{"la": "mao"}],
            },
            format="json",
        )
        request.user = my_user
        response = self.view(
            request, my_workflow_engagement.id, my_workflow_engagement_detail.id
        )

        self.assertEqual(response.status_code, 400)

    def test_patch__valid_payload_with_schema_existing_response_fails(self):
        """Patch current engagement to the one specified. If an old response fails schema validation, return error."""
        my_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(
                                            json_schema={
                                                "type": "object",
                                                "description": "A schema representing a single choice question user input.",
                                                "required": ["label", "inputOptions"],
                                                "properties": {
                                                    "id": {
                                                        "type": "string",
                                                        "title": "A string-based user input identifier.",
                                                        "description": "This value may be managed outside of the object specification and so is optional.",
                                                        "examples": [
                                                            "4125-1351-1251-asfd"
                                                        ],
                                                    },
                                                    "label": {
                                                        "type": "string",
                                                        "title": "UI Label for Input",
                                                        "description": "Label that should be displayed by user interfaces for this input.",
                                                        "examples": [
                                                            "The label to display for the input/question."
                                                        ],
                                                    },
                                                    "inputOptions": {
                                                        "$id": "#/properties/options",
                                                        "type": "array",
                                                        "title": "Question Options",
                                                        "description": "The options to be displayed to the user for this question.",
                                                        "minItems": 2,
                                                        "uniqueItems": True,
                                                        "items": {
                                                            "anyOf": [
                                                                {"type": "number"},
                                                                {"type": "string"},
                                                            ]
                                                        },
                                                    },
                                                    "correctInput": {
                                                        "description": "Indicates which answer is the correct one.",
                                                        "anyOf": [
                                                            {"type": "string"},
                                                            {"type": "number"},
                                                        ],
                                                    },
                                                    "meta": {
                                                        "type": "object",
                                                        "properties": {
                                                            "inputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not an answer should be required from the user.",
                                                            },
                                                            "correctInputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not the correct answer should be required from the user.",
                                                            },
                                                        },
                                                    },
                                                },
                                            }
                                        ),
                                        "specification": {
                                            "label": "What is your favorite number?",
                                            "inputOptions": [1, 2, 3, 4, 5],
                                            "correctInput": 1,
                                            "meta": {
                                                "inputRequired": True,
                                                "correctInputRequired": False,
                                            },
                                        },
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        )
        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_step_input.type.name = "single_choice_question"
        my_step_input.save()
        my_user = UserFactory()
        my_workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=my_collection,
            user=my_user,
        )
        my_workflow_engagement_detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=my_workflow_engagement,
            step=my_step,
            started=timezone.now(),
            finished=timezone.now(),
            user_responses=[
                {
                    "inputs": [
                        {
                            "stepInputID": str(my_step_input.id),
                            "stepInputUIIdentifier": str(my_step_input.ui_identifier),
                            "userInput": 1,
                        }
                    ]
                }
            ],
        )

        time_stamp = timezone.now()
        request = self.factory.patch(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/{my_workflow_engagement_detail.id}/",
            data={
                "finished": time_stamp,
                "user_responses": [
                    {
                        "inputs": [
                            {
                                "stepInputUIIdentifier": str(
                                    my_step_input.ui_identifier
                                ),
                                "userInput": 7,
                            }
                        ],
                        "submittedTime": time_stamp,
                    },
                    {
                        "inputs": [
                            {
                                "stepInputID": str(my_step_input.id),
                                "stepInputUIIdentifier": str(
                                    my_step_input.ui_identifier
                                ),
                                "userInput": 2,
                            }
                        ]
                    },
                ],
            },
            format="json",
        )
        request.user = my_user
        response = self.view(
            request, my_workflow_engagement.id, my_workflow_engagement_detail.id
        )
        self.assertEqual(response.status_code, 400)
