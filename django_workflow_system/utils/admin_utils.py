from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from ..models import WorkflowCollection, WorkflowCollectionMember


class EditLinkToInlineObject(object):
    """
    Adapted from https://stackoverflow.com/a/22113967/5666845

    Usage:

    @admin.register(MyModel)
    class MyModelAdmin:
        pass

    class MyModelInline(EditLinkToInlineObject, admin.TabularInline):
        model = MyModel
        readonly_fields = ('edit_link', )

    @admin.register(MySecondModel)
    class MySecondModelAdmin(admin.ModelAdmin):
        inlines = (MyModelInline, )

    """

    def edit_link(self, instance):
        url = reverse(
            "admin:%s_%s_change"
            % (instance._meta.app_label, instance._meta.model_name),
            args=[instance.pk],
        )
        if instance.pk:
            return mark_safe('<a href="{u}" target="_blank">edit</a>'.format(u=url))
        else:
            return ""


class MeOrAllFilter(admin.SimpleListFilter):
    """
    Users can filter Models with a `user` field by the current user, or all users

    Usage:
        import MeOrAllFilter and add it to the ModelAdmin's list_filter

    Example:
    ```
    @admin.register(MyModel)
    class MyModelAdmin(admin.ModelAdmin):
        list_filter = [MeOrAllFilter,]
    ```

    """

    # based on https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
    title = "User"
    parameter_name = "just_me"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin):
        return [("true", "Just Me")]  # 'All' option automatically provided

    def queryset(self, request: HttpRequest, queryset: QuerySet):
        if self.value() == "true":
            queryset = queryset.filter(user=request.user)
        return queryset


# TODO (low priority): there's a more django-ic way to do this
def is_null_filter_factory(field: str):
    """
    Creates a filter for is/is not null for the specified field
    A proper FieldListFilter would do something a little more complicated
    usage:

    @admin.register(ActivityAssignment)
    class ActivityAssignmentAdmin(admin.ModelAdmin):
        list_display = [...]
        readonly_fields = [...]
        list_filter = [
            ('actual_end', admin.DateFieldListFilter),
            ('activity', admin.RelatedFieldListFilter),
            is_null_filter_factory('response'),
        ]

    """

    class IsNullFilter(admin.SimpleListFilter):
        # based on https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
        title = f"{field} is null"
        parameter_name = f"{field}__isnull"

        def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin):
            return [("null", "Is Null"), ("not_null", "Is not Null")]

        def queryset(self, request: HttpRequest, queryset: QuerySet):
            if self.value() == "null":
                queryset = queryset.filter(**{field + "__isnull": True})
            elif self.value() == "not_null":
                queryset = queryset.exclude(**{field + "__isnull": True})
            return queryset

    return IsNullFilter


class StepInCollectionFilter(admin.SimpleListFilter):
    """
    Creates a filter for finding Steps that belong to a collection.
    The models do not provide a direct link from a step to a
    collection, so something this filter is needed.

    usage:

    @admin.register(WorkflowStep)
    class WorkflowStepAdmin(admin.ModelAdmin):
        list_display = [...]
        readonly_fields = [...]
        list_filter = [WorkflowStepCollectionFilter,]
    """

    title = "Collection"
    parameter_name = "collection"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin):
        qs = WorkflowCollection.objects.all()
        return [(o.id, o.name) for o in list(qs)]

    def queryset(self, request: HttpRequest, queryset: QuerySet):
        collection_id = request.GET.get("collection")
        members = WorkflowCollectionMember.objects.filter(
            workflow_collection=collection_id
        )
        workflow_ids = [o.workflow for o in list(members)]

        if len(workflow_ids) > 0:
            queryset = queryset.filter(workflow__in=workflow_ids)
        return queryset


class IsActiveCollectionFilter(admin.SimpleListFilter):
    """
    Creates a pass through filter for the sole purpose of renaming the filter names
    from 'yes', 'no' to 'Active', 'Inactive'

    usage:

    @admin.register(WorkflowCollection)
    class WorkflowCollection(admin.ModelAdmin):
        ...
        list_filter = [IsActiveCollectionFilter, ...]
    """

    title = "Active"
    parameter_name = "active"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin):
        return [(1, "Active"), (0, "Inactive")]

    def queryset(self, request: HttpRequest, queryset: QuerySet):
        active = request.GET.get("active")
        if active is not None:
            try:
                queryset = queryset.filter(active__exact=int(active))
            except:
                # nothing to handle - probably user entered junk into the address  bar
                pass
        return queryset


USER_SEARCH_FIELDS = (
    "user__username",
    "user__first_name",
    "user__last_name",
    "user__email",
)
