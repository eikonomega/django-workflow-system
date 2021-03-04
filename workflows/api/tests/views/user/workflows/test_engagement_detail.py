# import dateutil.parser
#
# from django.utils import timezone
# from django.test import TestCase
# from rest_framework import status
#
# from rest_framework.test import APIRequestFactory
#
# from website.api_v3.tests.factories import (
#     UserFactory, WorkflowCollectionFactory, WorkflowCollectionEngagementFactory,
#     WorkflowCollectionEngagementDetailFactory)
#
# from website.api_v3.tests.factories.workflows import json_schema
# from website.api_v3.views.user.workflows import (
#     WorkflowCollectionEngagementDetailsView,
#     WorkflowCollectionEngagementDetailView)
# from website.workflows.models import WorkflowStep, WorkflowStepInput, WorkflowCollection
import dateutil
from django.test import TestCase
from django.utils import timezone
from rest_framework import status

from rest_framework.test import APIRequestFactory

from workflows.api.tests.factories import (WorkflowCollectionFactory, UserFactory,
                                           WorkflowCollectionEngagementFactory,
                                           WorkflowCollectionEngagementDetailFactory)
from workflows.api.tests.factories.workflows import json_schema
from workflows.api.views.user.workflows import (WorkflowCollectionEngagementDetailsView,
                                                WorkflowCollectionEngagementDetailView)
from workflows.models import WorkflowCollection, WorkflowStep, WorkflowStepInput


class TestWorkflowEngagementDetailsView(TestCase):
    def setUp(self):
        self.view = WorkflowCollectionEngagementDetailsView.as_view()
        self.factory = APIRequestFactory()

        self.single_activity_collection: WorkflowCollection = WorkflowCollectionFactory(**{
            'category': 'ACTIVITY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowsteptext_set': [{
                        'content': "You did it"
                    }]
                }]
            }]
        })

        self.single_activity_collection__workflow = self.single_activity_collection.workflowcollectionmember_set.get().workflow
        self.single_activity_collection__step = self.single_activity_collection__workflow.workflowstep_set.get()

        self.single_survey_collection: WorkflowCollection = WorkflowCollectionFactory(**{
            'category': 'SURVEY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowstepinput_set': [{
                        'content': "whatever",
                        'required': True,
                        'response_schema': json_schema.JSONSchemaOneToFiveFactory(),
                    }]
                }]
            }]
        })
        self.single_survey_collection__workflow = self.single_survey_collection.workflowcollectionmember_set.get().workflow
        self.single_survey_collection__step = self.single_survey_collection__workflow.workflowstep_set.get()
        self.single_survey_collection__input = self.single_survey_collection__step.workflowstepinput_set.get()



        self.user_with_activity_engagement = UserFactory()
        self.user_with_activity_engagement__engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=self.single_activity_collection,
            user=self.user_with_activity_engagement,
        )
        self.user_with_activity_engagement__detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=self.user_with_activity_engagement__engagement,
            step=self.single_activity_collection__step,
        )

    def test_get__user_has_no_engagement_details(self):
        """
        Return a 200 (Empty dict) if requesting user has no engagement
        details.
        """
        request = self.factory.get(
            f"/users/self/workflows/engagements/{self.user_with_activity_engagement__engagement.id}/details/")
        request.user = UserFactory()
        response = self.view(request, self.user_with_activity_engagement__engagement.id)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data)

    def test_get__user_has_engagement_details(self):
        """Return engagement details for the requesting user."""
        request = self.factory.get(
            f"/users/self/workflows/engagements/{self.user_with_activity_engagement__engagement.id}/details/")
        request.user = self.user_with_activity_engagement
        response = self.view(request, self.user_with_activity_engagement__engagement.id)

        self.assertEqual(response.status_code, 200)
        for result in response.data:
            self.assertCountEqual(
                list(result.keys()),
                ['detail', 'step', 'user_response', 'started', 'finished'])
            self.assertEqual(
                result['detail'],
                f"http://testserver/workflow_system/users/self/workflows/engagements/"
                f"{self.user_with_activity_engagement__engagement.id}/details/"
                f"{self.user_with_activity_engagement__detail.id}/")
            self.assertEqual(
                result['step'],
                self.single_activity_collection__step.id)
            self.assertEqual(
                dateutil.parser.parse(result['started']),
                self.user_with_activity_engagement__detail.started)

    def test_post__incomplete_payload(self):
        """Incomplete JSON payload returns a 400 error."""
        user = UserFactory()
        wce = WorkflowCollectionEngagementFactory(
            workflow_collection=self.single_activity_collection,
            user=user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{wce.id}/details/",
            data={},
            format='json')
        request.user = user
        response = self.view(request, wce.id)

        self.assertEqual(response.status_code, 400)

    def test_post__duplicate_payload(self):
        """Duplicate JSON payload returns a 409."""
        request = self.factory.post(
            f"/users/self/workflows/engagements/{self.user_with_activity_engagement__engagement.id}/details/",
            data={
                'workflow_collection_engagement': f"http://testserver/workflow_system/users/self/workflows/engagements/{self.user_with_activity_engagement__engagement.id}/",
                'step': self.single_activity_collection__step.id,
                'started': timezone.now()
            },
            format='json')
        request.user = self.user_with_activity_engagement
        response = self.view(request, self.user_with_activity_engagement__engagement.id)

        self.assertEqual(response.status_code, 409)

    def test_post__valid_payload(self):
        """Valid JSON payload returns a 201."""

        user=UserFactory()
        wce = WorkflowCollectionEngagementFactory(
            workflow_collection=self.single_activity_collection,
            user=user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{wce.id}/details/",
            data={
                'workflow_collection_engagement':
                    f"http://testserver/workflow_system/users/self/workflows/engagements/{wce.id}/",
                'step': self.single_activity_collection__step.id,
                'started': timezone.now()
            },
            format='json')
        request.user = user
        response = self.view(request, wce.id)

        self.assertEqual(response.status_code, 201)

        self.assertEqual(response.data['state']['next_step_id'], self.single_activity_collection__step.id)

        self.assertEqual(
            response.data['state']['next_workflow'],
            f"http://testserver/workflow_system/workflows/{self.single_activity_collection__workflow.id}/")

    def test_post__not_in_collection(self):
        """Should not accept post if step is not in collection"""

        user=UserFactory()
        wce = WorkflowCollectionEngagementFactory(
            workflow_collection=self.single_activity_collection,
            user=user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{wce.id}/details/",
            data={
                'workflow_collection_engagement':
                    f"http://testserver/api_v3/users/self/workflows/engagements/{wce.id}/",
                'step': self.single_survey_collection__step.id,
                'started': timezone.now()
            },
            format='json')
        request.user = user
        response = self.view(request, wce.id)

        self.assertEqual(response.status_code, 400)

    def test_post__not_finished(self):
        """Valid JSON payload returns a 201 when unfinished."""

        user = UserFactory()
        wce = WorkflowCollectionEngagementFactory(
            workflow_collection=self.single_activity_collection,
            user=user,
        )

        request = self.factory.post(
            f"/users/self/workflows/engagements/{wce.id}/details/",
            data={
                'workflow_collection_engagement': f"http://testserver/workflow_system/users/self/workflows/engagements/{wce.id}/",
                'step': self.single_activity_collection__step.id,
                'started': timezone.now(),
                'finished': None,
            },
            format='json')
        request.user = self.user_with_activity_engagement
        response = self.view(request, wce.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['state']['next_step_id'], self.single_activity_collection__step.id)

        self.assertEqual(
            response.data['state']['next_workflow'],
            f"http://testserver/workflow_system/workflows/{self.single_activity_collection__workflow.id}/")

    def test_post__required_inputs_no_user_response(self):
        """Step has required inputs but no user_response in request, returns a 400."""

        my_user = UserFactory()
        my_workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=self.single_survey_collection,
            user=my_user,
        )
        request = self.factory.post(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/",
            data={
                'workflow_collection_engagement': f"http://testserver/workflow_system/users/self/workflows/engagements/{my_workflow_engagement.id}/",
                'step': self.single_survey_collection__step.id,
                'started': timezone.now(),
                'finished': timezone.now() + timezone.timedelta(minutes=5),
                'user_response': None,
            },
            format='json')
        request.user = self.user_with_activity_engagement
        response = self.view(request, my_workflow_engagement.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_no_required_inputs_questions_not_in_parsed(self):
        """No required questions, but "questions" is not in user_response json structure"""

        my_collection = WorkflowCollectionFactory(**{
            'category': 'SURVEY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowstepinput_set': [{
                        'content': "whatever",
                        'required': False
                    }]
                }]
            }]
        })

        my_step = WorkflowStep.objects.get(workflow__workflowcollectionmember__workflow_collection=my_collection)
        my_step_input = WorkflowStepInput.objects.get(workflow_step=my_step)
        my_user = UserFactory()
        my_workflow_engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=my_collection,
            user=my_user,
        )

        request = self.factory.post(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/",
            data={
                'workflow_collection_engagement': f"http://testserver/workflow_system/users/self/workflows/engagements/{my_workflow_engagement.id}/",
                'step': my_step.id,
                'started': timezone.now(),
                'finished': timezone.now() + timezone.timedelta(minutes=5),
                'user_response': {"ignored_key": "ignored value"},
            },
            format='json')
        request.user = my_user
        response = self.view(request, my_workflow_engagement.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['state']['next_step_id'], None)

        self.assertEqual(response.data['state']['next_workflow'], None)

    def test_post_assignment_next_step_started_on_second_workflow(self):
        """
        In an ACTIVITY workflowCollection
        Workflow1
            Step1
        Workflow2
            Step1 <- user starts here, submits a post
            Step2 <- next step should be here
        """
        collection_factory_spec = {
            "name": "two_workflow_survey",
            "category": "ACTIVITY",
            "workflow_set": [
                {
                    "name": "workflow_1",
                    "workflowstep_set": [
                        {
                            "code": "step1",
                            "workflowsteptext_set": [{
                                "content": "Who careeees, skip this"
                            }]
                        }
                    ]
                },
                {
                    "name": "workflow_2",
                    "workflowstep_set": [
                        {
                            "code": "step1",
                            "workflowsteptext_set": [{
                                "content": "setup of joke"
                            }]
                        },
                        {
                            "code": "step2",
                            "workflowsteptext_set": [{
                                "content": "punchline of joke"
                            }]
                        }
                    ]
                }
            ]
        }
        collection = WorkflowCollectionFactory(**collection_factory_spec)
        user = UserFactory()
        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=user,
        )
        workflow2 = collection.workflowcollectionmember_set.order_by('order')[1].workflow
        step1, step2 = tuple(workflow2.workflowstep_set.order_by('order'))
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                'workflow_collection_engagement':
                    f"http://testserver/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                'step': step1.id,
                'started': timezone.now(),
                'finished': timezone.now() + timezone.timedelta(milliseconds=1),
            },
            format='json')
        request.user = user
        response = WorkflowCollectionEngagementDetailsView.as_view()(request, engagement.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['state']['next_workflow'],
            f"http://testserver/workflow_system/workflows/{workflow2.id}/")
        self.assertEqual(response.data['state']['next_step_id'], step2.id)

    def test_post_survey_must_be_started_on_first_step(self):
        """
        In an SURVEY workflowCollection
        Workflow <- user starts here, submits a post
            Step2 <- If the user submits this first, that's an error
        """
        collection_factory_spec = {
            "name": "two_workflow_survey",
            "category": "ACTIVITY",
            "workflow_set": [
                {
                    "name": "workflow_1",
                    "workflowstep_set": [
                        {
                            "code": "step1",
                            "workflowsteptext_set": [{
                                "content": "Who careeees, skip this"
                            }]
                        },
                        {
                            "code": "step2",
                            "workflowsteptext_set": [{
                                "content": "punchline of joke"
                            }]
                        }
                    ]
                }
            ]
        }
        collection = WorkflowCollectionFactory(**collection_factory_spec)
        user = UserFactory()
        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=user,
        )
        workflow = collection.workflowcollectionmember_set.all()[0].workflow
        step1, step2 = tuple(workflow.workflowstep_set.order_by('order'))
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                'workflow_collection_engagement':
                    f"http://testserver/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                'step': step2.id,
                'started': timezone.now(),
                'finished': timezone.now() + timezone.timedelta(milliseconds=1),
            },
            format='json')
        request.user = user
        response = WorkflowCollectionEngagementDetailsView.as_view()(request, engagement.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_survey_cant_start_on_second_workflow(self):
        """
        In an ACTIVITY workflowCollection
        Workflow1
            Step1
        Workflow2
            Step1 <- user starts here, submits a post
            Step2 <- next step should be here
        """
        collection_factory_spec = {
            "name": "two_workflow_survey",
            "category": "SURVEY",
            "workflow_set": [
                {
                    "name": "workflow_1",
                    "workflowstep_set": [
                        {
                            "code": "step1",
                            "workflowsteptext_set": [{
                                "content": "Who careeees, skip this"
                            }]
                        }
                    ]
                },
                {
                    "name": "workflow_2",
                    "workflowstep_set": [
                        {
                            "code": "step1",
                            "workflowsteptext_set": [{
                                "content": "setup of joke"
                            }]
                        },
                        {
                            "code": "step2",
                            "workflowsteptext_set": [{
                                "content": "punchline of joke"
                            }]
                        }
                    ]
                }
            ]
        }
        collection = WorkflowCollectionFactory(**collection_factory_spec)
        user = UserFactory()
        engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=collection,
            user=user,
        )
        workflow2 = collection.workflowcollectionmember_set.order_by('order')[1].workflow
        step1, step2 = tuple(workflow2.workflowstep_set.order_by('order'))
        request = self.factory.post(
            f"/users/self/workflows/engagements/{engagement.id}/details/",
            data={
                'workflow_collection_engagement':
                    f"http://testserver/workflow_system/users/self/workflows/engagements/{engagement.id}/",
                'step': step1.id,
                'started': timezone.now(),
                'finished': timezone.now() + timezone.timedelta(milliseconds=1),
            },
            format='json')
        request.user = user
        response = WorkflowCollectionEngagementDetailsView.as_view()(request, engagement.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestWorkflowCollectionEngagementDetailView(TestCase):

    def setUp(self):
        self.view = WorkflowCollectionEngagementDetailView.as_view()
        self.factory = APIRequestFactory()
        self.single_activity_collection: WorkflowCollection = WorkflowCollectionFactory(**{
            'category': 'ACTIVITY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowsteptext_set': [{
                        'content': "You did it"
                    }]
                }]
            }]
        })
        self.single_activity_collection__workflow = self.single_activity_collection.workflowcollectionmember_set.get().workflow
        self.single_activity_collection__step = self.single_activity_collection__workflow.workflowstep_set.get()

        self.user_with_engagement = UserFactory()
        self.user_with_engagement__engagement = WorkflowCollectionEngagementFactory(
            workflow_collection=self.single_activity_collection,
            user=self.user_with_engagement,
        )
        self.user_with_engagement__detail = WorkflowCollectionEngagementDetailFactory(
            workflow_collection_engagement=self.user_with_engagement__engagement,
            step=self.single_activity_collection__step,
        )

    def test_get__engagement_does_not_exist(self):
        """
        Trying to use GET with an engagement id that doesn't exist
        results in 404 NOT FOUND
        """
        user = UserFactory()
        engagement = WorkflowCollectionEngagementFactory(
            user=user,
            workflow_collection=self.single_activity_collection,
        )

        fake_uuid = '027c315e-3788-4c30-8c58-46723077e2f0'
        request = self.factory.get(
            f"/users/self/workflows/engagements/{engagement.id}/details/{fake_uuid}/")
        request.user = UserFactory()
        response = self.view(request, engagement.id, fake_uuid)

        self.assertEqual(response.status_code, 404)

    def test_get__user_does_not_own_engagement(self):
        """
        Return 404 if user requests engagement they do not own,
        shows as NOT FOUND.
        """
        request = self.factory.get(
            f"/users/self/workflows/engagements/{self.user_with_engagement__engagement.id}/details/{self.user_with_engagement__detail.id}/")
        request.user = UserFactory()
        response = self.view(
            request,
            self.user_with_engagement__engagement.id,
            self.user_with_engagement__detail.id)

        self.assertEqual(response.status_code, 404)

    def test_get__authenticated_engagement(self):
        """Returned specified engagement for requesting user."""
        request = self.factory.get(
            f"/users/self/workflows/engagements/{self.user_with_engagement__engagement.id}/details/{self.user_with_engagement__detail.id}/")
        request.user = self.user_with_engagement
        response = self.view(request,
                             self.user_with_engagement__engagement.id,
                             self.user_with_engagement__detail.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['detail'],
            f"http://testserver/workflow_system/users/self/workflows/engagements/{self.user_with_engagement__engagement.id}/details/{self.user_with_engagement__detail.id}/")

    def test_patch__unauthenticated_engagement(self):
        """Return 404 error if trying to patch unknown engagement."""
        fake_uuid = '4f84f799-9cc5-43d3-0000-24840b7eb8ce'

        request = self.factory.patch(
            f"/users/self/workflows/engagements/{self.user_with_engagement__engagement.id}/details/{fake_uuid}/",
            data={},
            format='json')
        request.user = self.user_with_engagement
        response = self.view(request, self.user_with_engagement__engagement.id, fake_uuid)

        self.assertEqual(response.status_code, 404)

    def test_patch__valid_payload(self):
        """Patch current engagement to the one specified."""
        time_stamp = timezone.now()
        request = self.factory.patch(
            f"/users/self/workflows/engagements/{self.user_with_engagement__engagement.id}/details/{self.user_with_engagement__engagement.id}/",
            data={"finished": time_stamp,},
            format='json')
        request.user = self.user_with_engagement
        response = self.view(request,
                             self.user_with_engagement__engagement.id,
                             self.user_with_engagement__detail.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(dateutil.parser.parse(
            response.data['finished']), time_stamp)

    def test_patch__valid_payload_with_schema(self):
        """Patch current engagement to the one specified."""
        my_collection = WorkflowCollectionFactory(**{
            'category': 'SURVEY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowstepinput_set': [{
                        'content': "one to fiveeee",
                        'required': True,
                        "response_schema": json_schema.JSONSchemaOneToFiveFactory()
                    }]
                }]
            }]
        })
        my_step = WorkflowStep.objects.get(workflow__workflowcollectionmember__workflow_collection=my_collection)
        my_step_input = WorkflowStepInput.objects.get(workflow_step=my_step)
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
                'user_response': {
                    "questions": [{
                        "stepInputID": str(my_step_input.id),
                        "stepInputUIIdentifier": str(my_step_input.ui_identifier),
                        "response": 1
                    }]
                }
            },
            format='json')
        request.user = my_user
        response = self.view(
            request,
            my_workflow_engagement.id,
            my_workflow_engagement_detail.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(dateutil.parser.parse(
            response.data['finished']), time_stamp)

    def test_patch__valid_payload_with_schema_existing_response(self):
        """Patch current engagement to the one specified."""
        my_collection = WorkflowCollectionFactory(**{
            'category': 'SURVEY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowstepinput_set': [{
                        'content': "one to fiveeee",
                        'required': True,
                        "response_schema": json_schema.JSONSchemaOneToFiveFactory()
                    }]
                }]
            }]
        })
        my_step = WorkflowStep.objects.get(workflow__workflowcollectionmember__workflow_collection=my_collection)
        my_step_input = WorkflowStepInput.objects.get(workflow_step=my_step)
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
            user_response={"questions": [{
                "stepInputID": str(my_step_input.id),
                "stepInputUIIdentifier": str(my_step_input.ui_identifier),
                "response": 1
            }]}
        )

        time_stamp = timezone.now()
        request = self.factory.patch(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/{my_workflow_engagement_detail.id}/",
            data={
                "finished": time_stamp,
                'user_response': {
                    "questions": [{
                        "stepInputID": str(my_step_input.id),
                        "stepInputUIIdentifier": str(my_step_input.ui_identifier),
                        "response": 2
                    }]
                }
            },
            format='json')
        request.user = my_user
        response = self.view(
            request,
            my_workflow_engagement.id,
            my_workflow_engagement_detail.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(dateutil.parser.parse(
            response.data['finished']), time_stamp)

    def test_patch__schema_fails(self):
        """Patch current engagement to the one specified."""
        my_collection = WorkflowCollectionFactory(**{
            'category': 'SURVEY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowstepinput_set': [{
                        'content': "one to fiveeee",
                        'required': True,
                        "response_schema": json_schema.JSONSchemaOneToFiveFactory()
                    }]
                }]
            }]
        })
        my_step = WorkflowStep.objects.get(workflow__workflowcollectionmember__workflow_collection=my_collection)
        my_step_input = WorkflowStepInput.objects.get(workflow_step=my_step)
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
            user_response={"questions": [{
                "stepInputID": str(my_step_input.id),
                "stepInputUIIdentifier": str(my_step_input.ui_identifier),
                "response": 1
            }]}
        )
        time_stamp = timezone.now()
        request = self.factory.patch(
            f"/users/self/workflows/engagements/{my_workflow_engagement.id}/details/{my_workflow_engagement_detail.id}/",
            data={
                "finished": time_stamp,
                'user_response': {
                    "questions": [{
                        "stepInputID": str(my_step_input.id),
                        "stepInputUIIdentifier": str(my_step_input.ui_identifier),
                        "response": "africa"
                    }]
                }
            },
            format='json')
        request.user = my_user
        response = self.view(request,
                             my_workflow_engagement.id,
                             my_workflow_engagement_detail.id)

        self.assertEqual(response.status_code, 400)

    def test_post__answer_NOT_required_NOT_given(self):
        my_collection = WorkflowCollectionFactory(**{
            'category': 'SURVEY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowstepinput_set': [{
                        'content': "whatever",
                        'required': False
                    }]
                }]
            }]
        })

        my_step = WorkflowStep.objects.get(workflow__workflowcollectionmember__workflow_collection=my_collection)
        my_step_input = WorkflowStepInput.objects.get(workflow_step=my_step)
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
                'user_response': {"questions": []},
            },
            format='json')
        request.user = my_user
        response = self.view(
            request,
            my_workflow_engagement,
            my_workflow_engagement_detail.id
        )

        self.assertEqual(response.status_code, 200)

    def test_patch__answer_required_not_given(self):
        my_collection = WorkflowCollectionFactory(**{
            'category': 'SURVEY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowstepinput_set': [{
                        'content': "You DO need to answer 1 to 5",
                        'required': True,
                        "response_schema": json_schema.JSONSchemaOneToFiveFactory()
                    }]
                }]
            }]
        })

        my_step = WorkflowStep.objects.get(workflow__workflowcollectionmember__workflow_collection=my_collection)
        my_step_input = WorkflowStepInput.objects.get(workflow_step=my_step)
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
                'user_response': {"questions": []},
            },
            format='json')
        request.user = my_user
        response = self.view(request,
                             my_workflow_engagement.id,
                             my_workflow_engagement_detail.id)

        self.assertEqual(response.status_code, 400)

    def test_patch__questions_not_in_user_response(self):
        my_collection = WorkflowCollectionFactory(**{
            'category': 'SURVEY',
            "workflow_set": [{
                'workflowstep_set': [{
                    'workflowstepinput_set': [{
                        'content': "You DO need to answer 1 to 5",
                        'required': True,
                        "response_schema": json_schema.JSONSchemaOneToFiveFactory()
                    }]
                }]
            }]
        })

        my_step = WorkflowStep.objects.get(workflow__workflowcollectionmember__workflow_collection=my_collection)
        my_step_input = WorkflowStepInput.objects.get(workflow_step=my_step)
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
                'user_response': {"la": "mao"},
            },
            format='json')
        request.user = my_user
        response = self.view(request,
                             my_workflow_engagement.id,
                             my_workflow_engagement_detail.id)

        self.assertEqual(response.status_code, 400)
