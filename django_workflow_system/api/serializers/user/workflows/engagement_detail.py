"""DRF Serialzier Definition."""
from django.urls import reverse
import jsonschema
from rest_framework import serializers


from .....models import (
    WorkflowCollectionEngagementDetail,
    WorkflowStepUserInput,
    WorkflowStep,
    WorkflowCollection,
)


class WorkflowCollectionEngagementDetailSerializer(serializers.ModelSerializer):
    """
    Summary level serializer for WorkflowEngagementDetail objects.

    Notes:
        Because DRF does not natively support nested URL structures, I've
        had to hack this a bit to get the correct URL for the `detail`
        attribute.

        I believe there are better ways out there, but I'm not currently
        aware of what they may be. Feel free to improve.
    """

    detail = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowCollectionEngagementDetail
        fields = [
            "detail",
            "workflow_collection_engagement",
            "step",
            "user_responses",
            "started",
            "finished",
        ]
        # extra_kwargs = {"workflow_collection_engagement": {"write_only": True}}

    def get_detail(self, instance):
        reversed_url = reverse(
            viewname="user-workflow-collection-engagement-detail",
            kwargs={
                "engagement_id": instance.workflow_collection_engagement.id,
                "id": instance.id,
            },
        )

        return self.context["request"].build_absolute_uri(reversed_url)

    def validate(self, data):
        """Perform various validation checks."""

        def getattr_patched(attr_name):
            """
            This utility function retrieves 'attr_name' from data if it is present,
            otherwise it uses the value from self.instance. This is necessary because
            data will not have entries for all the fields in the Model
            if a partial update (PATCH) is performed.
            """
            if attr_name in data:
                return data[attr_name]
            if self.instance and hasattr(self.instance, attr_name):
                return getattr(self.instance, attr_name)
            return None

        step = getattr_patched("step")
        user_responses = getattr_patched("user_responses")

        has_required_inputs = bool(
            WorkflowStepUserInput.objects.filter(workflow_step=step, required=True)
        )

        workflow_collection_engagement = getattr_patched(
            "workflow_collection_engagement"
        )

        workflow_collection: WorkflowCollection = (
            workflow_collection_engagement.workflow_collection
        )

        state = workflow_collection_engagement.state

        # CHECK 1: Does the specified step belong to a workflow in the specified collection?
        if not workflow_collection.workflowcollectionmember_set.filter(
            workflow__workflowstep=step
        ):
            raise serializers.ValidationError(
                "Step must belong to a workflow in the collection"
            )

        # CHECK 2
        # Usually, the step must be either state['next_step_id'] or state['prev_step_id']
        # However, in an ACTIVITY workflow collection, if the user has not submitted any
        # engagement details, the step can be any first step of a workflow
        if workflow_collection.category == "ACTIVITY":
            existing_engagement_details = (
                workflow_collection_engagement.workflowcollectionengagementdetail_set.all()
            )
            if not existing_engagement_details:
                if WorkflowStep.objects.filter(
                    workflow=step.workflow, order__lt=step.order
                ):
                    raise serializers.ValidationError(
                        "Posted step must be the first step in a workflow"
                    )
            else:
                if step.id not in (state["next_step_id"], state["prev_step_id"]):
                    raise serializers.ValidationError(
                        "Posted step must be next step or previous step."
                    )
        elif workflow_collection.category == "SURVEY":
            if step.id not in (state["next_step_id"], state["prev_step_id"]):
                raise serializers.ValidationError(
                    "Posted step must be next step or previous step."
                )

            """EXAMPLE JSON PAYLOAD

            {
                "detail": "http://localhost:8000/api/workflow_system/users/self/workflows/engagements/6dfe24d5-9e2d-4308-9c33-e878a3d378b4/details/ad4e2263-d468-4adb-9c0a-b96740ccacd1/",
                "workflow_collection_engagement": "6dfe24d5-9e2d-4308-9c33-e878a3d378b4",
                "step": "353a1aba-57fd-4183-802e-083d53863601",
                "user_responses": [
                        {
                            "submittedTime": "2021-07-26 18:33:06.731050+00:00",
                            "inputs": [
                                {
                                    "stepInputID": "758f482d-3eb0-4779-bf2a-bad9e452ea0e", 
                                    "stepInputUIIdentifier": "question_1",
                                    "userInput": "Red"
                                },
                                {
                                    "stepInputID": "96e7f658-7f08-4432-b3d1-f483f01aa19b", 
                                    "stepInputUIIdentifier": "question_2",
                                    "userInput": false
                                },
                                {
                                    "stepInputID": "2312304f-ceb3-4fea-b93f-94420060b238", 
                                    "stepInputUIIdentifier": "question_3",
                                    "userInput": "hi"
                                }
                            ]
                        },
                        {
                            "submittedTime": "2021-07-26 18:33:06.731050+00:00",
                            "inputs": [
                                {
                                    "stepInputID": "758f482d-3eb0-4779-bf2a-bad9e452ea0e", 
                                    "stepInputUIIdentifier": "question_1",
                                    "userInput": "Red"
                                },
                                {
                                    "stepInputID": "96e7f658-7f08-4432-b3d1-f483f01aa19b", 
                                    "stepInputUIIdentifier": "question_2",
                                    "userInput": true
                                },
                                {
                                    "stepInputID": "2312304f-ceb3-4fea-b93f-94420060b238", 
                                    "stepInputUIIdentifier": "question_3",
                                    "userInput": "hi"
                                }
                            ]
                        }
                    ],
                "started": "2021-07-26T08:00:28-05:00",
                "finished": null
            }

            """

        # CHECK 4
        # 1: Ensure all required attributes are present for each question in the payload.
        # 2: Ensure user input data in payload corresponds to actual, defined user inputs for the step.
        # 3: Sorted user inputs for further validation in CHECK 5.
        collected_user_inputs_by_step_input_id = {}

        # Outer Loop: User Response Sets
        for index, user_input_set in enumerate(user_responses):

            # Inner Loop: Each Input in the Response Set
            for user_input in user_input_set["inputs"]:

                # Ensure required keys are present for each input.
                try:
                    step_input_id = user_input["stepInputID"]
                    step_input_UI_identifier = user_input["stepInputUIIdentifier"]
                    response = user_input["userInput"]
                except KeyError as e:
                    raise serializers.ValidationError(
                        "Missing key in questions entry {}".format(e.args[0])
                    )

                if not WorkflowStepUserInput.objects.filter(
                    id=step_input_id, ui_identifier=step_input_UI_identifier
                ):
                    raise serializers.ValidationError(
                        f"No step with given stepInputID {step_input_id} and stepInputUIIdentifier {step_input_UI_identifier} exists."
                    )

                # Add the user input to our sorted collection for further checks.
                if step_input_id not in collected_user_inputs_by_step_input_id.keys():
                    collected_user_inputs_by_step_input_id[step_input_id] = {}
                collected_user_inputs_by_step_input_id[step_input_id][
                    index
                ] = user_input

        # CHECK 5 - Final Checks
        # Evaluate each defined WorkflowStepUserInput object for the step
        # and make sure that required answers are present and conform
        # to the specification for the object.
        for step_input in WorkflowStepUserInput.objects.filter(workflow_step=step):
            step_input_id = str(step_input.id)

            # Determine if the user has one or more answers for the current WorkflowStepUserInput
            if step_input_id not in collected_user_inputs_by_step_input_id:
                # No answers. Now see if answers were required.
                if step_input.required:
                    raise serializers.ValidationError(
                        "A response is required, but missing, for step_input id {}".format(
                            step_input_id
                        )
                    )

            else:
                # TODO: This checking process, in general, could probably benefit
                # from a little bit of clean-up. This is too broad in that it will
                # handle both "incorrect" answers and radical schema violations in the same way.
                responses_to_input = collected_user_inputs_by_step_input_id[
                    step_input_id
                ]
                for index, response in responses_to_input.items():
                    try:
                        jsonschema.validate(
                            instance=response, schema=step_input.response_schema
                        )
                    except jsonschema.ValidationError:
                        # This answer is not valid
                        for entry in user_responses[index]["inputs"]:
                            if step_input_id == entry["stepInputID"]:
                                entry["is_valid"] = False
                                break
                    else:
                        # This is!
                        for entry in user_responses[index]["inputs"]:
                            if step_input_id == entry["stepInputID"]:
                                entry["is_valid"] = True
                                break

        return data
