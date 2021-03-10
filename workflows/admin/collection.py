"""
Admin interface implementation collection-related models
"""
from itertools import chain, count

from django.contrib import admin
from django.db import IntegrityError
from django.utils import timezone
from django.utils.safestring import mark_safe

from ..utils.admin_utils import IsActiveCollectionFilter
from ..models import (
    Workflow,
    WorkflowCollection,
    WorkflowCollectionMember,
    WorkflowCollectionTagOption,
    WorkflowStep,
    WorkflowStepDependencyGroup,
    WorkflowStepDependencyDetail,
    WorkflowCollectionAssignment, WorkflowCollectionEngagement,
    WorkflowCollectionTagAssignment)


@admin.register(WorkflowCollectionTagOption)
class WorkflowCollectionTagOptionAdmin(admin.ModelAdmin):
    list_display = ["text"]


class WorkflowCollectionMemberInline(admin.StackedInline):
    model = WorkflowCollectionMember
    extra = 1
    ordering = ["order"]

class WorkflowCollectionTagOptionInline(admin.StackedInline):
    model = WorkflowCollectionTagAssignment
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
    fieldsets = [
        (
            None,
            {
                "fields": [
                    ("name", "code", "version", "created_by"),
                    ("assignment_only", "recommendable", "active", "ordered"),
                    "description",
                    ("category",),
                    ("home_image_preview", "home_image"),
                    ("library_image_preview", "library_image"),
                    ("detail_image_preview", "detail_image"),
                ]
            },
        ),
    ]

    readonly_fields = [
        "home_image_preview",
        "library_image_preview",
        "detail_image_preview",
        "open_assignments",
        "open_subscriptions",
    ]

    inlines = [WorkflowCollectionTagOptionInline, WorkflowCollectionMemberInline]
    actions = ["copy", "deep_copy", "kill_stragglers"]
    list_filter = ["tags", IsActiveCollectionFilter]

    def home_image_preview(self, instance: WorkflowCollection):
        if instance.pk:
            return mark_safe(f"<img src={instance.home_image.url} />")
        else:
            return ""

    def library_image_preview(self, instance: WorkflowCollection):
        if instance.pk:
            return mark_safe(f"<img src={instance.library_image.url} />")
        else:
            return ""

    def detail_image_preview(self, instance: WorkflowCollection):
        if instance.pk:
            return mark_safe(f"<img src={instance.detail_image.url} />")
        else:
            return ""

    def open_assignments(self, instance: WorkflowCollection):
        return instance.workflowcollectionassignment_set.filter(
            status__in=(
                WorkflowCollectionAssignment.ASSIGNED,
                WorkflowCollectionAssignment.IN_PROGRESS
            )
        ).count()

    def open_subscriptions(self, instance: WorkflowCollection):
        return instance.workflowcollectionsubscription_set.filter(
            active=True
        ).count()

    def copy(self, request, queryset):
        """
        This method copies the workflow collection,
        it's LINKS to workflows,
        every dependency and dependency detail,
        and LINKS to tag_options
        """
        workflow_collection: WorkflowCollection
        for workflow_collection in queryset:
            old_workflow_collection = WorkflowCollection.objects.get(pk=workflow_collection.pk)
            workflow_collection.pk = None
            workflow_collection.code += '_copy'
            workflow_collection.name += ' (copy)'
            try:
                workflow_collection.save()  # our new collection gets a primary key here
            except IntegrityError:
                for num_existing_copies in count(1):
                    workflow_collection.code = '{}_copy_{}'.format(old_workflow_collection.code, num_existing_copies)
                    workflow_collection.name = '{} (copy {})'.format(old_workflow_collection.name, num_existing_copies)
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
            for workflow_step_dependency_group in old_workflow_collection.workflowstepdependencygroup_set.all():
                old_workflow_step_dependency_group = WorkflowStepDependencyGroup.objects.get(
                    pk=workflow_step_dependency_group.pk)
                workflow_step_dependency_group.pk = None
                workflow_step_dependency_group.workflow_collection = workflow_collection
                workflow_step_dependency_group.save()

                dependency_detail: WorkflowStepDependencyDetail
                for dependency_detail in old_workflow_step_dependency_group.workflowstepdependencydetail_set.all():
                    dependency_detail.id = None
                    dependency_detail.dependency_group = workflow_step_dependency_group
                    dependency_detail.save()

            workflow_collection.tags.set(old_workflow_collection.tags.all())

    copy.short_description = "Copy selected workflow collections"
    copy.allowed_permissions = ('add',)

    def deep_copy(self, request, queryset):
        """
        This method copies the workflow collection,
        makes COPIES of every workflow,
        every dependency and dependency detail,
        and LINKS to tag_options
        """
        workflow_collection: WorkflowCollection
        for workflow_collection in queryset:
            old_workflow_collection = WorkflowCollection.objects.get(pk=workflow_collection.pk)
            workflow_collection.pk = None
            workflow_collection.code += '_copy'
            workflow_collection.name += ' (copy)'
            try:
                workflow_collection.save()  # our new collection gets a primary key here
            except IntegrityError:
                for num_existing_copies in count(1):
                    workflow_collection.code = '{}_copy_{}'.format(old_workflow_collection.code, num_existing_copies)
                    workflow_collection.name = '{} (copy {})'.format(old_workflow_collection.name, num_existing_copies)
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
                new_workflow.code += '_copy'
                new_workflow.name += ' (copy)'
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

                    for data_group in old_step.data_groups.all():
                        step.data_groups.add(data_group)

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
                for workflow_step_dependency_group in old_workflow_collection.workflowstepdependencygroup_set.all():
                    old_workflow_step_dependency_group = WorkflowStepDependencyGroup.objects.get(
                        pk=workflow_step_dependency_group.pk)
                    workflow_step_dependency_group.pk = None
                    workflow_step_dependency_group.workflow_collection = workflow_collection
                    workflow_step_dependency_group.workflow_step = old_to_new_step[
                        workflow_step_dependency_group.workflow_step]
                    workflow_step_dependency_group.save()

                    dependency_detail: WorkflowStepDependencyDetail
                    for dependency_detail in old_workflow_step_dependency_group.workflowstepdependencydetail_set.all():
                        dependency_detail.id = None
                        dependency_detail.dependency_group = workflow_step_dependency_group
                        dependency_detail.dependency_step = old_to_new_step[dependency_detail.dependency_step]
                        dependency_detail.save()

            workflow_collection.tags.set(old_workflow_collection.tags.all())

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
                    WorkflowCollectionAssignment.IN_PROGRESS
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
