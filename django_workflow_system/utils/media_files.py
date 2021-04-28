"""Media files location specifications."""


def workflow_step_media_location(instance, filename):
    """Return the location of a stored media file for a Workflow Step."""
    workflow_id = instance.workflow_step.workflow.id
    step_id = instance.workflow_step_id
    ui_identifier = instance.ui_identifier
    file_extension = filename.rpartition(".")[2]

    return f"workflow_system/workflows/{workflow_id}/steps/{step_id}/{ui_identifier}.{file_extension}"


def collection_image_location(instance, filename):
    """Return the location of a stored media file for a Workflow Collection."""
    collection_id = instance.id
    image_type = instance.type
    file_extension = filename.rpartition(".")[2]

    return f"workflow_system/collections/{collection_id}/{image_type}.{file_extension}"


def workflow_image_location(instance, filename):
    """Return the location of a stored media file for a Workflow."""
    workflow_id = instance.id
    image_type = instance.type
    file_extension = filename.rpartition(".")[2]

    return f"workflow_system/workflows/{workflow_id}/{image_type}.{file_extension}"


def author_media_location(instance, filename):
    """Return the location of a stored media file for an Author."""
    author_id = instance.id
    image_type = filename.rpartition(".")[2]

    return f"workflow_system/authors/{author_id}/profileImage.{image_type}"
