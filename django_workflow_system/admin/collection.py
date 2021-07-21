"""Admin interface implementation collection-related models."""
from itertools import chain, count


from django.contrib import admin
from django.db import IntegrityError
from django.utils import timezone

from ..utils.admin_utils import IsActiveCollectionFilter
from ..models import (
    Workflow,
    WorkflowCollection,
    WorkflowCollectionMember,
    WorkflowStep,
    WorkflowStepDependencyGroup,
    WorkflowStepDependencyDetail,
    WorkflowCollectionAssignment,
    WorkflowCollectionEngagement,
    WorkflowCollectionImage,
)
from .collection_dependency import WorkflowCollectionDependencyInline


class WorkflowCollectionMemberInline(admin.StackedInline):
    model = WorkflowCollectionMember
    extra = 1
    ordering = ["order"]


class WorkflowCollectionImageInline(admin.StackedInline):
    model = WorkflowCollectionImage
    extra = 1


@admin.register(WorkflowCollection)
class WorkflowCollectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "version",
        "category",
        "ordered",
        "active",
        "open_assignments",
        "open_subscriptions",
    )
    filter_horizontal = ["metadata"]
    search_fields = ["name", "category"]

    # I don't know why this works
    # https://github.com/django/django/blob/1b4d1675b230cd6d47c2ffce41893d1881bf447b/django/contrib/auth/admin.py#L25
    # Line 31
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "metadata":
            qs = kwargs.get("queryset", db_field.remote_field.model.objects)
            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            kwargs["queryset"] = qs.select_related("parent_group")
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)

    fieldsets = [
        (
            None,
            {
                "fields": [
                    ("name", "code"),
                    ("version", "created_by"),
                    ("assignment_only", "recommendable", "active", "ordered"),
                    "description",
                    "category",
                    "metadata",
                ]
            },
        ),
    ]

    readonly_fields = [
        "open_assignments",
        "open_subscriptions",
    ]

    inlines = [
        WorkflowCollectionMemberInline,
        WorkflowCollectionImageInline,
        WorkflowCollectionDependencyInline,
    ]

    actions = ["copy", "deep_copy", "kill_stragglers"]
    list_filter = [IsActiveCollectionFilter]

    def open_assignments(self, instance: WorkflowCollection):
        return instance.workflowcollectionassignment_set.filter(
            status__in=(
                WorkflowCollectionAssignment.ASSIGNED,
                WorkflowCollectionAssignment.IN_PROGRESS,
            )
        ).count()

    def open_subscriptions(self, instance: WorkflowCollection):
        return instance.workflowcollectionsubscription_set.filter(active=True).count()

    def copy(self, request, queryset):
        """
        This method copies the workflow collection,
        it's LINKS to workflows,
        every dependency and dependency detail,
        and LINKS to metadata
        """
        workflow_collection: WorkflowCollection
        for workflow_collection in queryset:
            old_workflow_collection = WorkflowCollection.objects.get(
                pk=workflow_collection.pk
            )
            workflow_collection.pk = None
            workflow_collection.code += "_copy"
            workflow_collection.name += " (copy)"
            try:
                workflow_collection.save()  # our new collection gets a primary key here
            except IntegrityError:
                for num_existing_copies in count(1):
                    workflow_collection.code = "{}_copy_{}".format(
                        old_workflow_collection.code, num_existing_copies
                    )
                    workflow_collection.name = "{} (copy {})".format(
                        old_workflow_collection.name, num_existing_copies
                    )
                    try:
                        workflow_collection.save()
                    except IntegrityError:
                        pass
                    else:
                        break

            member: WorkflowCollectionMember
            for member in old_workflow_collection.workflowcollectionmember_set.all():
                member.pk = None
                member.workflow_collection = workflow_collection
                member.save()

            workflow_step_dependency_group: WorkflowStepDependencyGroup
            for (
                workflow_step_dependency_group
            ) in old_workflow_collection.workflowstepdependencygroup_set.all():
                old_workflow_step_dependency_group = (
                    WorkflowStepDependencyGroup.objects.get(
                        pk=workflow_step_dependency_group.pk
                    )
                )
                workflow_step_dependency_group.pk = None
                workflow_step_dependency_group.workflow_collection = workflow_collection
                workflow_step_dependency_group.save()

                dependency_detail: WorkflowStepDependencyDetail
                for (
                    dependency_detail
                ) in (
                    old_workflow_step_dependency_group.workflowstepdependencydetail_set.all()
                ):
                    dependency_detail.id = None
                    dependency_detail.dependency_group = workflow_step_dependency_group
                    dependency_detail.save()

            workflow_collection.metadata.set(old_workflow_collection.metadata.all())

    copy.short_description = "Copy selected workflow collections"
    copy.allowed_permissions = ("add",)

    def deep_copy(self, request, queryset):
        """
        This method copies the workflow collection,
        makes COPIES of every workflow,
        every dependency and dependency detail,
        and LINKS to metadata
        """
        workflow_collection: WorkflowCollection
        for workflow_collection in queryset:
            old_workflow_collection = WorkflowCollection.objects.get(
                pk=workflow_collection.pk
            )
            workflow_collection.pk = None
            workflow_collection.code += "_copy"
            workflow_collection.name += " (copy)"
            try:
                workflow_collection.save()  # our new collection gets a primary key here
            except IntegrityError:
                for num_existing_copies in count(1):
                    workflow_collection.code = "{}_copy_{}".format(
                        old_workflow_collection.code, num_existing_copies
                    )
                    workflow_collection.name = "{} (copy {})".format(
                        old_workflow_collection.name, num_existing_copies
                    )
                    try:
                        workflow_collection.save()
                    except IntegrityError:
                        pass
                    else:
                        break

            member: WorkflowCollectionMember
            for member in old_workflow_collection.workflowcollectionmember_set.all():

                old_workflow = Workflow.objects.get(pk=member.workflow.pk)
                new_workflow = Workflow.objects.get(pk=member.workflow.pk)

                new_workflow.pk = None
                new_workflow.code += "_copy"
                new_workflow.name += " (copy)"
                new_workflow.save()  # our new workflow gets a primary key here

                member.pk = None
                member.workflow = new_workflow
                member.workflow_collection = workflow_collection
                member.save()

                old_to_new_step = {}
                for step in old_workflow.workflowstep_set.all():
                    old_step = WorkflowStep.objects.get(pk=step.pk)
                    step.pk = None  # creates a new instance when saved
                    step.workflow = new_workflow
                    step.save()  # our new step gets a primary key here

                    old_to_new_step[old_step] = step

                    for metadata in old_step.metadata.all():
                        step.metadata.add(metadata)

                    step_media_iterator = chain(
                        old_step.workflowstepaudio_set.all(),
                        old_step.workflowstepvideo_set.all(),
                        old_step.workflowstepimage_set.all(),
                        old_step.workflowstepinput_set.all(),
                        old_step.workflowsteptext_set.all(),
                    )
                    for step_media in step_media_iterator:
                        step_media.pk = None  # creates a new instance when saved
                        step_media.workflow_step = step
                        step_media.save()  # our new step gets a primary key here

                workflow_step_dependency_group: WorkflowStepDependencyGroup
                for (
                    workflow_step_dependency_group
                ) in old_workflow_collection.workflowstepdependencygroup_set.all():
                    old_workflow_step_dependency_group = (
                        WorkflowStepDependencyGroup.objects.get(
                            pk=workflow_step_dependency_group.pk
                        )
                    )
                    workflow_step_dependency_group.pk = None
                    workflow_step_dependency_group.workflow_collection = (
                        workflow_collection
                    )
                    workflow_step_dependency_group.workflow_step = old_to_new_step[
                        workflow_step_dependency_group.workflow_step
                    ]
                    workflow_step_dependency_group.save()

                    dependency_detail: WorkflowStepDependencyDetail
                    for (
                        dependency_detail
                    ) in (
                        old_workflow_step_dependency_group.workflowstepdependencydetail_set.all()
                    ):
                        dependency_detail.id = None
                        dependency_detail.dependency_group = (
                            workflow_step_dependency_group
                        )
                        dependency_detail.dependency_step = old_to_new_step[
                            dependency_detail.dependency_step
                        ]
                        dependency_detail.save()

            workflow_collection.metadata.set(old_workflow_collection.metadata.all())

    deep_copy.short_description = "Copy selected workflow collections and its workflows"
    deep_copy.allowed_permissions = ("add",)

    def kill_stragglers(self, request, queryset):
        """
        This method closes/marks as finished/deactivates
        all Assignments, Engagements and Recommendations associated
        with this workflow collection.
        """
        now = timezone.now()

        workflow_collection: WorkflowCollection
        for workflow_collection in queryset:

            # close any open assignments and mark their engagements as complete
            workflow_collection.workflowcollectionassignment_set.filter(
                status__in=(
                    WorkflowCollectionAssignment.ASSIGNED,
                    WorkflowCollectionAssignment.IN_PROGRESS,
                )
            ).update(status=WorkflowCollectionAssignment.CLOSED_INCOMPLETE)

            WorkflowCollectionEngagement.objects.filter(
                finished__isnull=True,
                workflowcollectionassignment__status=WorkflowCollectionAssignment.CLOSED_INCOMPLETE,
            ).update(finished=now)

            # deactivate active workflow collection subscriptions
            workflow_collection.workflowcollectionsubscription_set.filter(
                active=True
            ).update(active=False)

    kill_stragglers.short_description = "Close Remaining Connections"
    kill_stragglers.allowed_permissions = ("change", "delete")
