from django.core.exceptions import ValidationError
from django.test import TestCase

from website.api_v3.tests.factories import WorkflowCollectionEngagementFactory, UserFactory, WorkflowCollectionFactory
from website.api_v3.tests.factories.workflows.json_schema import JSONSchemaOneToFiveFactory
from website.chronological_user_profiles.models import ChronologicalUserDataCategory
from website.workflows.models import WorkflowCollectionEngagementDetail


class TestGetResponse(TestCase):

    def setUp(self) -> None:
        self.user = UserFactory()

    @classmethod
    def setUpTestData(cls):
        ChronologicalUserDataCategory.objects.create(
            code="test_wellbeing_dimension",
            label="WellBeing Dimension",
        )

        cls.simple_survey__survey_collection = WorkflowCollectionFactory(**{
            "name": "simple_survey",
            "category": "SURVEY",
            "workflow_set": [{
                "name": "simple_survey_workflow",
                "code": "simple_survey_workflow",
                "workflowstep_set": [
                    {
                        "code": "industry",
                        "workflowstepinput_set": [{
                            "ui_identifier": "question_1",
                            "content": "what is 1+1?",
                            "response_schema": JSONSchemaOneToFiveFactory()
                        }]
                    },
                ]
            }]
        })

        cls.workflow = cls.simple_survey__survey_collection.workflowcollectionmember_set.get().workflow
        cls.step = cls.workflow.workflowstep_set.get()
        cls.input = cls.step.workflowstepinput_set.get()

    def test_get_response_sanity_check(self):
        wce = WorkflowCollectionEngagementFactory(
            user=self.user,
            workflow_collection=self.simple_survey__survey_collection,
            workflowcollectionengagementdetail_set=[{
                'step': self.step,
                'user_response': {"questions": [{
                    "stepInputID": str(self.input.id),
                    "stepInputUIIdentifier": str(self.input.ui_identifier),
                    "response": 2
                }]
                },
            }],
        )

        self.assertEqual(wce.get_response('industry', 'question_1'), 2)

    def test_get_response_bad_ui_identifier(self):
        wce = WorkflowCollectionEngagementFactory(
            user=self.user,
            workflow_collection=self.simple_survey__survey_collection,
            workflowcollectionengagementdetail_set=[{
                'step': self.step,
                'user_response': {"questions": [{
                    "stepInputID": str(self.input.id),
                    "stepInputUIIdentifier": str(self.input.ui_identifier),
                    "response": 2
                }]
                },
            }],
        )
        with self.assertRaises(WorkflowCollectionEngagementDetail.DoesNotExist):
            wce.get_response('industry', 'not a ui identifier')
