"""DRF Serialzier Definition."""
import logging

from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from rest_framework import serializers

from .....models import WorkflowCollection, WorkflowCollectionEngagement
from .engagement_detail import WorkflowCollectionEngagementDetailSerializer

logger = logging.getLogger(__name__)


class WorkflowCollectionEngagementBaseSerializer(serializers.ModelSerializer):
    """Base serializer for common methods/fields between Detailed and Summary serializers"""

    def validate(self, data):
        """
        Check that the user does not have an existing unfinished engagement for the same
        workflow collection, also ensure that the finish date is later than
        the start date.
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

        started = getattr_patched("started")
        finished = getattr_patched("finished")
        workflow_collection = getattr_patched("workflow_collection")
        state = getattr_patched("state")
        workflowcollectionassignment = getattr_patched("workflowcollectionassignment")
        user = getattr_patched("user")
        # Check that the finish date is later than the start date.

        if finished is not None:
            if finished < started:
                raise serializers.ValidationError(
                    "The finish date must be later than the start date."
                )
            if workflow_collection.category == "SURVEY":
                if state[
                    "next_step_id"
                ]:  # i.e. there is still a next step which can be completed
                    raise serializers.ValidationError(
                        "There are still steps which can be completed"
                    )

        if workflowcollectionassignment:
            if workflow_collection != workflowcollectionassignment.workflow_collection:
                raise serializers.ValidationError(
                    "The Engagement and Assignment "
                    "WorkflowCollections are not the same"
                )
            elif user != workflowcollectionassignment.user:
                raise serializers.ValidationError(
                    "The Engagement and Assignment Users are not the same"
                )
        # Check if the user has an existing incomplete engagement to the same workflow collection

        existing_engagement = WorkflowCollectionEngagement.objects.filter(
            user=user,
            workflow_collection=workflow_collection,
            finished__isnull=True,
        )
        if self.instance:
            existing_engagement = existing_engagement.exclude(pk=self.instance.pk)
        if existing_engagement:
            raise serializers.ValidationError(
                "The user has an existing incomplete engagement for this workflow collection."
            )

        if finished is not None:
            # Clean the finished engagement by deleting unfinished details
            self.instance.workflowcollectionengagementdetail_set.filter(
                finished=None
            ).delete()
        return data

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(), write_only=True
    )

    workflow_collection = serializers.HyperlinkedRelatedField(
        queryset=WorkflowCollection.objects.all(),
        view_name="workflow-collection",
        lookup_field="id",
    )

    state = serializers.SerializerMethodField(required=False)

    class Meta:
        model = WorkflowCollectionEngagement
        fields = [
            "user",
            "workflow_collection",
            "started",
            "finished",
            "state",
        ]

    def get_state(self, instance):
        """
        Translate the `state` property that exists on
        WorkflowCollectionEngagement objects to a API
        friendly representation.

        This is needed to have the representation include
        the fully hyperlink necessary for "dumb" clients.

        Parameters:
            instance (WorkflowCollectionEngagement): The object being serialized.

        Returns:
            dict: Hyperlinked `state` property dictionary.
        """

        def workflow_to_uri(workflow_id):
            if workflow_id is None:
                return None
            try:
                reversed_url = reverse(viewname="workflow", kwargs={"id": workflow_id})

            except NoReverseMatch as e:
                logger.error(
                    f"Could not reverse workflow {workflow_id}",
                    exc_info=e,
                    extra={"workflow_id": workflow_id},
                )
                return None
            return self.context["request"].build_absolute_uri(reversed_url)

        state = instance.state
        formatted_previously_completed_workflows = []
        for previously_completed_workflow in state["previously_completed_workflows"]:
            uri = workflow_to_uri(previously_completed_workflow["workflow_id"])
            if uri:
                formatted_previously_completed_workflows.append({"workflow": uri})

        state["next_workflow"] = workflow_to_uri(state.pop("next_workflow_id"))
        state["prev_workflow"] = workflow_to_uri(state.pop("prev_workflow_id"))
        state[
            "previously_completed_workflows"
        ] = formatted_previously_completed_workflows

        return state


class WorkflowCollectionEngagementSerializer(
    WorkflowCollectionEngagementBaseSerializer
):
    """
    Summary level Serializer for WorkflowCollectionEngagement objects.
    """

    detail = serializers.HyperlinkedIdentityField(
        view_name="user-workflow-collection-engagement",
        lookup_field="id",
        required=False,
    )

    class Meta:
        model = WorkflowCollectionEngagement
        fields = [
            "detail",
            "user",
            "workflow_collection",
            "started",
            "finished",
        ]


class WorkflowCollectionEngagementAndDetailsSerializer(
    WorkflowCollectionEngagementSerializer
):
    """
    Summary level Serializer for WorkflowCollectionEngagementDetail objects.
    """

    workflowcollectionengagementdetail_set = (
        WorkflowCollectionEngagementDetailSerializer(
            many=True,
            required=False,
        )
    )

    class Meta:
        model = WorkflowCollectionEngagement
        fields = [
            "detail",
            "user",
            "workflow_collection",
            "started",
            "finished",
            "workflowcollectionengagementdetail_set",
        ]


class WorkflowCollectionEngagementDetailedSerializer(
    WorkflowCollectionEngagementBaseSerializer
):
    """
    Detailed serializer for WorkflowCollectionEngagement objects.

    Notes:
        It is easy to confuse this with a serializer for the
        WorkflowUserEngagementDetail class, but it is not.

        It is rather, a "detailed" serializer for the
        WorkflowUserEngagement class.
    """

    workflowcollectionengagementdetail_set = (
        WorkflowCollectionEngagementDetailSerializer(
            many=True,
            required=False,
        )
    )

    self_detail = serializers.HyperlinkedIdentityField(
        view_name="user-workflow-collection-engagement",
        lookup_field="id",
        required=False,
    )

    class Meta:
        model = WorkflowCollectionEngagement
        fields = [
            "self_detail",
            "user",
            "workflow_collection",
            "started",
            "finished",
            "workflowcollectionengagementdetail_set",
            "state",
        ]
