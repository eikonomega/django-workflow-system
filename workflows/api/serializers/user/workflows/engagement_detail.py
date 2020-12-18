import jsonschema
from django.urls import reverse

from rest_framework import serializers

from .....models import (
    WorkflowCollectionEngagementDetail,
    WorkflowStepInput,
    WorkflowStep,
    WorkflowCollection,
)


class WorkflowCollectionEngagementDetailSummarySerializer(serializers.ModelSerializer):
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
            'detail',
            'workflow_collection_engagement',
            'step',
            'user_response',
            'started',
            'finished'
        ]
        extra_kwargs = {'workflow_collection_engagement': {'write_only': True}}

    def get_detail(self, instance):
        reversed_url = reverse(
            viewname='user-workflow-collection-engagement-detail-v3',
            kwargs={
                'engagement_id': instance.workflow_collection_engagement.id,
                'id': instance.id
            }
        )

        return self.context['request'].build_absolute_uri(reversed_url)

    def validate(self, data):
        """
        First, we check if the the step being submitted is allowed in the state model.
        In order to maintain consistent state, a user can only submit an engagement for
        a step if it is the previous step or the next step, or it is the first step
        submitted in an activity-type collection engagement and it is the first step of a workflow

        Check that user_response has a valid entry for each WorkflowStepInput
        according to that WorkflowStepInput's JSON Schema validator.

        If a user is not finished:
            then we don't care about the state of user_response

        Regarding finished workflow_collection_engagements:
            If the workflow_step has required inputs:
                then user_response must contain something to be valid
            Else the workflow_step does not have required inputs,
                then having no answers is automatically valid,

            For each stepInput:
                if the user did not give an answer
                    then that's an error if the question was required
                if the user gave an answer
                    it must be valid, regardless of whether the question was required or not
        """

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

        step = getattr_patched('step')
        finished = getattr_patched('finished')
        user_response = getattr_patched('user_response')
        has_required_inputs = bool(WorkflowStepInput.objects.filter(workflow_step=step, required=True))
        workflow_collection_engagement = getattr_patched('workflow_collection_engagement')
        workflow_collection: WorkflowCollection = workflow_collection_engagement.workflow_collection

        state = workflow_collection_engagement.state

        if not workflow_collection.workflowcollectionmember_set.filter(workflow__workflowstep=step):
            raise serializers.ValidationError('Step must belong to a workflow in the collection')

        # Usually, the step must be either state['next_step_id'] or state['prev_step_id']
        # However, in an ACTIVITY workflow collection, if the user has not submitted any
        # engagement details, the step can be any first step of a workflow
        if workflow_collection.category == 'ACTIVITY':
            existing_engagement_details = workflow_collection_engagement.workflowcollectionengagementdetail_set.all()
            if not existing_engagement_details:
                if WorkflowStep.objects.filter(workflow=step.workflow, order__lt=step.order):
                    raise serializers.ValidationError("Posted step must be the first step in a workflow")
            else:
                if step.id not in (state['next_step_id'], state['prev_step_id']):
                    raise serializers.ValidationError("Posted step must be next step or previous step.")
        elif workflow_collection.category == 'SURVEY':
            if step.id not in (state['next_step_id'], state['prev_step_id']):
                raise serializers.ValidationError("Posted step must be next step or previous step.")

        if not finished:
            return data

        if has_required_inputs:  # then having no answers is bad
            if not user_response:
                raise serializers.ValidationError("workflow_step has required step_input(s) but "
                                                  "workflow_collection_engagement has no user_response")
            if "questions" not in user_response:
                raise serializers.ValidationError("workflow_step has required step_input(s) but "
                                                  "user_response does not contain key \"questions\"")
        else:  # having no answers is ok
            if not user_response:
                return data
            if "questions" not in user_response:
                return data

        # Ensure all required attributes are present for each question in the payload.
        answer_dict = {}
        for answer in user_response["questions"]:
            try:
                step_input_id = answer["stepInputID"]
                step_input_UI_identifier = answer["stepInputUIIdentifier"]
                response = answer["response"]
            except KeyError as e:
                raise serializers.ValidationError('Missing key in questions entry {}'.format(e.args[0]))
            if not WorkflowStepInput.objects.filter(id=step_input_id, ui_identifier=step_input_UI_identifier):
                raise serializers.ValidationError('No step with given stepInputID and stepInputUIIdentifier exists')
            answer_dict[step_input_id] = response


        for step_input in WorkflowStepInput.objects.filter(workflow_step=step):
            step_input_id = str(step_input.id)
            if step_input_id not in answer_dict:  # if user did not give an answer...
                if step_input.required:  # that's a problem if it was required
                    raise serializers.ValidationError('Missing response to step_input id {}'.format(step_input_id))
            else:  # user gave an answer, and we should validate it
                response = answer_dict[step_input_id]
                try:
                    jsonschema.validate(instance=response, schema=step_input.response_schema.schema)
                except jsonschema.ValidationError as e:
                    raise serializers.ValidationError(
                        'Response did not match workflow step input response schema {}'.format(e.message))
        return data
