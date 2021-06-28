from rest_framework.request import Request


def strip_sensitive_data(data: dict):
    """
    Function that strips request data before it is sent to our graylog server.
    """
    sensitive_keys = ("password", "response", "user_responses")

    # don't overwrite request!
    data = dict(data)

    # Scrub Request Data
    for key in sensitive_keys:
        if key in data:
            data[key] = "[CENSORED]"

    return str(data)


def find_property(property, *source_list, default):
    """
    Searches through a list of objects for one having the given property with a non-none
    value.
    Parameters
    ----------
    property
        name of the property
    source_list
        list of objects to search through
    default
        default value for the property

    Returns
    -------
    the first found value of the property, if found
    """
    if default:
        return default
    for source in source_list:
        if source is not None and getattr(source, property, None):
            return getattr(source, property)


def generate_extra(
    *,  # the following must be presented as keyword args
    event_code=None,
    request: Request = None,
    user=None,
    activity=None,
    activity_assignment=None,
    workflow_collection=None,
    workflow_collection_assignment=None,
    workflow_collection_engagement=None,
    workflow_collection_engagement_detail=None,
    workflow_collection_subscription=None,
    serializer_errors=None,
    **kwargs,
):
    """
    Extracts useful information from WW objects into a flat dict for GELF logging.

    Parameters
    ----------
    event_code: str
        a static code representing the type of event which occured
    request: Request
        a request
    user: User
        a user
    activity: Activity
        a map your day activity
    activity_assignment: ActivityAssignment
        a map your day activity assignment
    workflow_collection: WorkflowCollection
        a workflow collection
    workflow_collection_assignment: WorkflowCollectionAssignment
        a workflow collection assignment
    workflow_collection_engagement: WorkflowCollectionEngagement
        a workflow collection engagement
    workflow_collection_engagement_detail: WorkflowCollectionEngagementDetail
        a workflow collection engagement detail
    workflow_collection_subscription: WorkflowCollectionSubscription
        a workflow collection subscription
    serializer_errors:
        serializer errors
    kwargs
        any additional arguments

    Returns
    -------
    extra: dict

    """
    extra = dict(kwargs)
    if event_code:
        extra["event_code"] = event_code
    if serializer_errors:
        extra["serializer_errors"] = serializer_errors

    # automatically add missing info
    workflow_collection_engagement = find_property(
        "workflow_collection_engagement",
        workflow_collection_engagement_detail,
        default=workflow_collection_engagement,
    )
    workflow_collection = find_property(
        "workflow_collection",
        workflow_collection_assignment,
        workflow_collection_subscription,
        workflow_collection_engagement,
        default=workflow_collection,
    )
    activity = find_property(
        "activity",
        activity_assignment,
        default=activity,
    )

    user = find_property(
        "user",
        request,
        workflow_collection_assignment,
        workflow_collection_subscription,
        workflow_collection_engagement,
        activity_assignment,
        default=user,
    )

    # handle request
    if request:
        extra["request__path"] = request.path
        extra["request__method"] = request.method
        if hasattr(request, "query_params") and request.query_params:
            extra["request__query_params"] = request.query_params
        if hasattr(request, "data") and request.data:
            extra["request__data"] = strip_sensitive_data(request.data)
    # handle user
    if user:
        extra["user__username"] = user.username
        extra["user__id"] = user.id

    if activity:
        extra["activity__id"] = activity.id
        extra["activity__name"] = activity.name

    if activity_assignment:
        extra["activity_assignment__id"] = activity_assignment.id
        extra[
            "activity_assignment__associated_date"
        ] = activity_assignment.associated_date

    if workflow_collection:
        extra["workflow_collection__id"] = workflow_collection.id
        extra["workflow_collection__code"] = workflow_collection.code
        extra["workflow_collection__version"] = workflow_collection.version
        extra["workflow_collection__category"] = workflow_collection.category

    if workflow_collection_assignment:
        extra["workflow_collection_assignment__id"] = workflow_collection_assignment.id
        extra[
            "workflow_collection_assignment__start"
        ] = workflow_collection_assignment.start
        extra[
            "workflow_collection_assignment__status"
        ] = workflow_collection_assignment.status

    if workflow_collection_engagement:
        extra["workflow_collection_engagement__id"] = workflow_collection_engagement.id
        extra[
            "workflow_collection_engagement__started"
        ] = workflow_collection_engagement.started
        extra[
            "workflow_collection_engagement__finished"
        ] = workflow_collection_engagement.finished

    if workflow_collection_engagement_detail:
        extra[
            "workflow_collection_engagement_detail__id"
        ] = workflow_collection_engagement_detail.id
        extra[
            "workflow_collection_engagement_detail__step__code"
        ] = workflow_collection_engagement_detail.step.code
        extra[
            "workflow_collection_engagement_detail__started"
        ] = workflow_collection_engagement_detail.started
        extra[
            "workflow_collection_engagement_detail__finished"
        ] = workflow_collection_engagement_detail.finished

    if workflow_collection_subscription:
        extra[
            "workflow_collection_subscription__id"
        ] = workflow_collection_subscription.id
        extra[
            "workflow_collection_subscription__active"
        ] = workflow_collection_subscription.active

    return extra
