"""
Admin interface implementation for every workflow model not deserving of its own file
"""
from itertools import chain, count

from django.contrib import admin
from django.db import IntegrityError
from django.db.models import Case, When, Value, IntegerField, QuerySet, Count
from django.http import HttpRequest
from django.utils.safestring import mark_safe

from ..utils.admin_utils import (
    EditLinkToInlineObject,
    MeOrAllFilter,
    USER_SEARCH_FIELDS,
)
from ..models import (
    JSONSchema,
    Workflow,
    WorkflowAuthor,
    WorkflowCollectionAssignment,
    WorkflowStep,
    WorkflowCollectionMember,
    WorkflowCollectionSubscription,
    WorkflowCollectionSubscriptionSchedule,
    WorkflowCollectionEngagement,
    WorkflowCollectionEngagementDetail,
    WorkflowMetadata,
    WorkflowCollectionImageType,
    WorkflowImageType,
    WorkflowImage,
    WorkflowCollectionRecommendation,
)

# assignment.py


@admin.register(WorkflowCollectionAssignment)
class WorkflowCollectionAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "workflow_collection",
        "user",
        "start",
        "status",
        "engagement",
    ]
    list_filter = [MeOrAllFilter, "workflow_collection", "status"]
    search_fields = USER_SEARCH_FIELDS + ("workflow_collection__code",)

    readonly_fields = ["engagement"]


# author.py


@admin.register(WorkflowAuthor)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("user", "title")
    list_editable = ["title"]
    search_fields = USER_SEARCH_FIELDS


def make_ordering():
    """
    Let's break this down:
    `Case` acts like a if/elif/elif/elif/else statement on the SQL side
    Each case is represented by a `When` object.
    This particular Case statement assigns to each WorkflowMetadata an integer
    based on the number of non-null parents it has. We'll call this generation number
    The order of the WSDGs is decided first by the reverse numerical order generation number,
    then by the name of the WSDG.

    ```
    ordering = [
        Case(
            When(parent_group=None, then=1),
            When(parent_group__parent_group=None, then=2),
            When(parent_group__parent_group__parent_group=None, then=3),
            When(parent_group__parent_group__parent_group__parent_group=None, then=4),
            # and so on
            default=Value(99),
            output_field=IntegerField()
        ).desc(),
        'name'
    ]
    ```

    https://docs.djangoproject.com/en/2.2/ref/models/options/#ordering
    https://docs.djangoproject.com/en/2.2/ref/models/conditional-expressions/
    """
    case_args = []
    for i in range(1, 10):
        when_args = {"__".join(["parent_group"] * i): None, "then": Value(i)}
        case_args.append(When(**when_args))
    return [
        Case(*case_args, default=Value(99), output_field=IntegerField()).desc(),
        "name",
    ]


@admin.register(WorkflowMetadata)
class WorkflowMetadataAdmin(admin.ModelAdmin):
    list_display = ["name", "full_path"]
    readonly_fields = ["full_path"]
    ordering = make_ordering()
    search_fields = ["name", "parent_group__name"]


# engagement.py


class WorkflowCollectionEngagementDetailInline(
    EditLinkToInlineObject, admin.TabularInline
):
    model = WorkflowCollectionEngagementDetail
    extra = 0
    fields = (
        "step",
        "started",
        "finished",
        "user_responses",
        "edit_link",
    )
    readonly_fields = (
        "step",
        "started",
        "finished",
        "user_responses",
        "edit_link",
    )


class IsFinishedFilter(admin.SimpleListFilter):
    # based on https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
    title = "Is Finished"
    parameter_name = "finished"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin):
        return [("true", "True"), ("false", "False")]

    def queryset(self, request: HttpRequest, queryset: QuerySet):
        if self.value() == "true":
            queryset = queryset.filter(finished__isnull=False)
        elif self.value() == "false":
            queryset = queryset.filter(finished__isnull=True)
        return queryset


class HasDetailsFilter(admin.SimpleListFilter):
    # based on https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
    title = "Has Details"
    parameter_name = "has_details"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin):
        return [("true", "True"), ("false", "False")]

    def queryset(self, request: HttpRequest, queryset: QuerySet):
        if self.value() == "true":
            queryset = queryset.annotate(
                Count("workflowcollectionengagementdetail")
            ).exclude(workflowcollectionengagementdetail__count=0)
        elif self.value() == "false":
            queryset = queryset.annotate(
                Count("workflowcollectionengagementdetail")
            ).filter(workflowcollectionengagementdetail__count=0)
        return queryset


@admin.register(WorkflowCollectionEngagement)
class WorkflowCollectionEngagementAdmin(admin.ModelAdmin):
    list_display = ["workflow_collection", "user", "started", "finished"]
    list_filter = [
        "workflow_collection",
        IsFinishedFilter,
        HasDetailsFilter,
        MeOrAllFilter,
    ]
    inlines = [WorkflowCollectionEngagementDetailInline]
    search_fields = USER_SEARCH_FIELDS


@admin.register(WorkflowCollectionEngagementDetail)
class WorkflowCollectionEngagementDetailAdmin(admin.ModelAdmin):
    list_display = [
        "workflow_collection_engagement",
        "user",
        "step",
        "started",
        "finished",
    ]
    search_fields = [
        "workflow_collection_engagement__" + field for field in USER_SEARCH_FIELDS
    ] + [
        "workflow_collection_engagement__workflow_collection__code",
    ]

    def user(self, obj: WorkflowCollectionEngagementDetail):
        return obj.workflow_collection_engagement.user.username

    user.admin_order_field = "workflow_collection_engagement__user__username"
    user.short_description = "User"


# json_schema.py


@admin.register(JSONSchema)
class JSONSchemaAdmin(admin.ModelAdmin):
    list_display = ["code", "description"]
    ordering = ["code"]


# subscription


class WorkflowCollectionSubscriptionScheduleInline(admin.TabularInline):
    model = WorkflowCollectionSubscriptionSchedule


@admin.register(WorkflowCollectionSubscription)
class WorkflowCollectionSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["workflow_collection", "user", "active"]
    inlines = [WorkflowCollectionSubscriptionScheduleInline]
    list_filter = ["active", "workflow_collection"]
    search_fields = USER_SEARCH_FIELDS + ("workflow_collection__code",)


# workflow.py


class StepInLine(EditLinkToInlineObject, admin.StackedInline):
    model = WorkflowStep
    extra = 1
    readonly_fields = ("edit_link",)
    filter_horizontal = ["metadata"]
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


class WorkflowImageInline(admin.StackedInline):
    model = WorkflowImage
    extra = 1


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "author", "category"]
    inlines = [StepInLine, WorkflowImageInline]
    actions = ["copy"]
    list_filter = [
        "workflowcollectionmember__workflow_collection",
        "workflowcollectionmember__workflow_collection__category",
    ]
    filter_horizontal = ["metadata"]
    search_fields = ["name", "code"] + [
        "author__" + field for field in USER_SEARCH_FIELDS
    ]
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

    fields = [
        "code",
        "name",
        "version",
        "image_preview",
        "author",
        "created_by",
        "metadata",
    ]
    readonly_fields = ["image_preview"]

    def category(self, obj):
        member = WorkflowCollectionMember.objects.filter(workflow=obj)
        # NOTE(Adam): I found that some workflows belong to more than one collection, and thus may have
        #             multiple categories as well. I think it might be best to add category as a 1-n column?
        return ", ".join(set(map(lambda m: m.workflow_collection.category, member)))

    def image_preview(self, instance: Workflow):
        if instance.pk:
            return mark_safe(f"<img src={instance.image.url} />")
        else:
            return ""

    def copy(self, request, queryset):
        workflow: Workflow
        for workflow in queryset:
            old_workflow = Workflow.objects.get(pk=workflow.pk)
            workflow.pk = None
            workflow.code += "_copy"
            workflow.name += " (copy)"
            try:
                workflow.save()  # our new workflow gets a primary key here
            except IntegrityError:
                for num_existing_copies in count(1):
                    workflow.code = "{}_copy_{}".format(
                        old_workflow.code, num_existing_copies
                    )
                    workflow.name = "{} (copy {})".format(
                        old_workflow.name, num_existing_copies
                    )
                    try:
                        workflow.save()
                    except IntegrityError:
                        pass
                    else:
                        break

            for step in old_workflow.workflowstep_set.all():
                old_step = WorkflowStep.objects.get(pk=step.pk)
                step.pk = None  # creates a new instance when saved
                step.workflow = workflow
                step.save()  # our new step gets a primary key here

                for metadata in old_step.metadata.all():
                    step.metadata.add(metadata)

                step_media_iterator = chain(
                    old_step.workflowstepaudio_set.all(),
                    old_step.workflowstepvideo_set.all(),
                    old_step.workflowstepimage_set.all(),
                    old_step.workflowstepuserinput_set.all(),
                    old_step.workflowsteptext_set.all(),
                )
                for step_media in step_media_iterator:
                    step_media.pk = None  # creates a new instance when saved
                    step_media.workflow_step = step
                    step_media.save()  # our new step gets a primary key here

    copy.short_description = "Copy selected workflows"
    copy.allowed_permissions = ("add",)


# collection_image_type.py


@admin.register(WorkflowCollectionImageType)
class WorkflowCollectionImageTypeAdmin(admin.ModelAdmin):
    list_display = ["type"]


# workflow_image_type.py


@admin.register(WorkflowImageType)
class WorkflowImageTypeAdmin(admin.ModelAdmin):
    list_display = ["type"]


@admin.register(WorkflowCollectionRecommendation)
class WorkflowCollectionRecommendationAdmin(admin.ModelAdmin):
    list_display = ["user", "workflow_collection", "start", "end"]
    ordering = ["user"]
    search_fields = USER_SEARCH_FIELDS + ("workflow_collection__code",)
