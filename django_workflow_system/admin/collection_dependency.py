"""Django admin panel configuration."""
from django.contrib import admin

from ..models import WorkflowCollectionDependency


@admin.register(WorkflowCollectionDependency)
class WorkflowCollectionDependencyAdmin(admin.ModelAdmin):
    list_display = [
        "source",
        "target",
    ]


class WorkflowCollectionDependencyInline(admin.StackedInline):
    model = WorkflowCollectionDependency
    extra = 1
    fk_name = "source"
