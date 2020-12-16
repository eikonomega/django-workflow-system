"""
Admin interface setup for workflow feature/app.
"""


from django.contrib import admin

from workflows.models import (
    JSONSchema,
    Workflow,
    WorkflowAuthor,
    WorkflowCollectionAssignment,
    WorkflowCollection,
    WorkflowCollectionMember,
    WorkflowCollectionTagOption,
    WorkflowStep,
    WorkflowStepInput,
    WorkflowStepAudio,
    WorkflowStepImage,
    WorkflowStepText,
    WorkflowStepVideo,
    WorkflowCollectionSubscription,
    WorkflowCollectionSubscriptionSchedule,
    WorkflowStepUITemplate,
    WorkflowCollectionEngagement,
    WorkflowCollectionEngagementDetail,
    WorkflowStepDependencyGroup,
    WorkflowStepDependencyDetail)


class StepInLine(admin.StackedInline):
    model = WorkflowStep
    extra = 1


class SteptextInline(admin.TabularInline):
    model = WorkflowStepText
    extra = 1


class StepInputInLine(admin.TabularInline):
    model = WorkflowStepInput
    extra = 1


class StepAudioInline(admin.TabularInline):
    model = WorkflowStepAudio
    extra = 1


class StepImageInline(admin.TabularInline):
    model = WorkflowStepImage
    extra = 1


class StepVideoInline(admin.TabularInline):
    model = WorkflowStepVideo
    extra = 1


class WorkflowCollectionMemberInline(admin.StackedInline):
    model = WorkflowCollectionMember
    extra = 1


class WorkflowCollectionAssignmentInline(admin.StackedInline):
    model = WorkflowCollectionAssignment


class WorkflowCollectionSubscriptionSchedule(admin.TabularInline):
    model = WorkflowCollectionSubscriptionSchedule


# adminModel Definitions
@admin.register(WorkflowAuthor)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'title')
    list_editable = ['title']


@admin.register(WorkflowCollectionTagOption)
class WorkflowCollectionTagOptionAdmin(admin.ModelAdmin):
    list_display = ['text']


@admin.register(WorkflowCollection)
class WorkflowCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'ordered')
    inlines = [
        WorkflowCollectionMemberInline]


@admin.register(WorkflowStepUITemplate)
class WorkflowUITemplateAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(JSONSchema)
class JSONSchemaAdmin(admin.ModelAdmin):
    list_display = ["code", "description"]


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'author', 'on_completion']
    inlines = [StepInLine]


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'code', 'order', 'ui_template']
    inlines = [
        StepInputInLine,
        SteptextInline,
        StepImageInline,
        StepAudioInline,
        StepVideoInline,
    ]


@admin.register(WorkflowCollectionAssignment)
class WorkflowCollectionAssignmentAdmin(admin.ModelAdmin):
    list_display = ["workflow_collection", "user", "assigned_on",
                    "status", "engagement"]


@admin.register(WorkflowCollectionSubscription)
class WorkflowCollectionSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["workflow_collection", "user", "active"]
    inlines = [WorkflowCollectionSubscriptionSchedule]


@admin.register(WorkflowStepDependencyGroup)
class WorkflowStepDependencyGroupAdmin(admin.ModelAdmin):
    list_display = ['workflow_step', 'workflow_collection']


@admin.register(WorkflowStepDependencyDetail)
class WorkflowStepDependencyDetailAdmin(admin.ModelAdmin):
    list_display = ['dependency_group', 'dependency_step']


@admin.register(WorkflowCollectionEngagement)
class WorkflowUserEngagementAdmin(admin.ModelAdmin):
    list_display = ['workflow_collection', 'user', 'started',
                    'finished']


@admin.register(WorkflowCollectionEngagementDetail)
class WorkflowUserEngagementDetailAdmin(admin.ModelAdmin):
    list_display = ['workflow_collection_engagement',
                    'step', 'started', 'finished']
