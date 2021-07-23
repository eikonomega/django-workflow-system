"""
Admin interface implementation step-related models
"""
from itertools import chain, count
from typing import Optional

from django import forms
from django.contrib import admin
from django.db import IntegrityError
from django.db.models import OuterRef, Subquery

from ..utils.admin_utils import StepInCollectionFilter

from ..models import (
    WorkflowCollection,
    WorkflowStep,
    WorkflowStepUserInput,
    WorkflowStepUserInputType,
    WorkflowStepAudio,
    WorkflowStepExternalLink,
    WorkflowStepImage,
    WorkflowStepText,
    WorkflowStepVideo,
    WorkflowStepUITemplate,
    WorkflowStepDependencyGroup,
    WorkflowStepDependencyDetail,
)


class StepTextForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = WorkflowStepText
        fields = ["ui_identifier", "text"]


class SteptextInline(admin.TabularInline):
    model = WorkflowStepText
    extra = 1
    form = StepTextForm


class StepUserInputForm(forms.ModelForm):
    class Meta:
        model = WorkflowStepUserInput
        fields = ["ui_identifier", "required", "type", "specification"]

    class Media:
        js = ("admin/js/jquery.init.js",)


class StepUserInputInLine(admin.TabularInline):
    model = WorkflowStepUserInput
    extra = 1
    form = StepUserInputForm


class StepAudioInline(admin.TabularInline):
    model = WorkflowStepAudio
    extra = 1


class StepImageInline(admin.TabularInline):
    model = WorkflowStepImage
    extra = 1


class StepVideoInline(admin.TabularInline):
    model = WorkflowStepVideo
    extra = 1


class StepExternalLinkInline(admin.TabularInline):
    model = WorkflowStepExternalLink
    extra = 1


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ["workflow", "code", "order", "ui_template"]
    inlines = [
        StepUserInputInLine,
        SteptextInline,
        StepImageInline,
        StepAudioInline,
        StepVideoInline,
        StepExternalLinkInline,
    ]
    actions = ["copy"]
    list_filter = ["workflow", StepInCollectionFilter]
    filter_horizontal = ["metadata"]
    search_fields = ["code", "workflow__name", "workflow__code", "ui_template__name"]
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

    fields = ["workflow", "code", "order", "ui_template", "metadata"]

    def copy(self, request, queryset):
        step: WorkflowStep
        for step in queryset:
            old_step = WorkflowStep.objects.get(pk=step.pk)
            step.pk = None  # creates a new instance when saved
            max_order = step.workflow.workflowstep_set.order_by("-order")[0].order
            step.order = max_order + 1
            step.code += "_copy"
            try:
                step.save()  # our new step gets a primary key here
            except IntegrityError:
                for num_existing_copies in count(1):
                    step.code = "{}_copy_{}".format(old_step.code, num_existing_copies)
                    try:
                        step.save()
                    except IntegrityError:
                        pass
                    else:
                        break
            for metadata in old_step.metadata.all():
                step.metadata.add(metadata)

            step_media_iterator = chain(
                old_step.workflowstepaudio_set.all(),
                old_step.workflowstepvideo_set.all(),
                old_step.workflowstepimage_set.all(),
                old_step.workflowstepuserinput_set.all(),
                old_step.workflowsteptext_set.all(),
                old_step.workflowstepexternallink_set.all(),
            )
            for step_media in step_media_iterator:
                step_media.pk = None  # creates a new instance when saved
                step_media.workflow_step = step
                step_media.save()  # our new step gets a primary key here

    copy.short_description = "Copy selected steps"
    copy.allowed_permissions = ("add",)


@admin.register(WorkflowStepUITemplate)
class WorkflowUITemplateAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


class WorkflowStepDependencyDetailInLineFormSet(forms.BaseInlineFormSet):
    """
    A custom InLineFormSet which passes the parent WorkflowStepDependencyGroup instance
    as the parameter to the __init__ of WorkflowStepDependencyDetailInLineForm
    so that each WorkflowStepDependencyDetailInLineForm can restrict the available steps to
    steps in the parent WorkflowStepDependencyGroup's workflow_collection
    """

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["parent_object"] = self.instance
        return kwargs


class WorkflowStepDependencyDetailInLineForm(forms.ModelForm):
    class Meta:
        model = WorkflowStepDependencyDetail
        fields = ["dependency_step", "required_response"]

    def __init__(self, *args, **kwargs):
        parent_object: Optional[WorkflowStepDependencyGroup] = kwargs.pop(
            "parent_object", None
        )
        super(WorkflowStepDependencyDetailInLineForm, self).__init__(*args, **kwargs)
        if parent_object:
            try:
                workflow_collection = parent_object.workflow_collection
            except WorkflowCollection.DoesNotExist:
                return
            step_to_member = workflow_collection.workflowcollectionmember_set.filter(
                workflow=OuterRef("workflow")
            )
            # take all steps\
            # in a workflow in the workflow collection
            # annotate the steps with the order of (a workflow_member (of their workflow) in the collection)
            # order first by the annotated wf_order, then the step's order in the workflow
            self.fields["dependency_step"].queryset = (
                WorkflowStep.objects.filter(
                    workflow__workflowcollectionmember__workflow_collection=workflow_collection
                )
                .annotate(wf_order=Subquery(step_to_member.values("order")[:1]))
                .order_by("wf_order", "order")
            )


class WorkflowStepDependencyDetailInline(admin.TabularInline):
    model = WorkflowStepDependencyDetail
    extra = 1
    formset = WorkflowStepDependencyDetailInLineFormSet
    form = WorkflowStepDependencyDetailInLineForm


class WorkflowStepDependencyGroupForm(forms.ModelForm):
    class Meta:
        model = WorkflowStepDependencyGroup
        fields = ["workflow_collection", "workflow_step"]

    def __init__(self, *args, **kwargs):
        super(WorkflowStepDependencyGroupForm, self).__init__(*args, **kwargs)
        if self.instance:
            try:
                workflow_collection = self.instance.workflow_collection
            except WorkflowCollection.DoesNotExist:
                return
            step_to_member = workflow_collection.workflowcollectionmember_set.filter(
                workflow=OuterRef("workflow")
            )
            self.fields["workflow_step"].queryset = (
                WorkflowStep.objects.filter(
                    workflow__workflowcollectionmember__workflow_collection=self.instance.workflow_collection
                )
                .annotate(wf_order=Subquery(step_to_member.values("order")[:1]))
                .order_by("wf_order", "order")
            )


@admin.register(WorkflowStepDependencyGroup)
class WorkflowStepDependencyGroupAdmin(admin.ModelAdmin):
    list_display = ["workflow_step", "workflow_collection"]
    inlines = [WorkflowStepDependencyDetailInline]
    form = WorkflowStepDependencyGroupForm


@admin.register(WorkflowStepDependencyDetail)
class WorkflowStepDependencyDetailAdmin(admin.ModelAdmin):
    list_display = ["dependency_group", "dependency_step"]


@admin.register(WorkflowStepUserInputType)
class WorkflowStepUserInputType(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
