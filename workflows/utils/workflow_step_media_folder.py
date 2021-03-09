def workflow_step_media_folder(instance, filename):
    return 'workflows/workflows/{}/steps/{}/{}.{}'.format(
        instance.workflow_step.workflow.id,
        instance.workflow_step_id,
        instance.ui_identifier,
        filename.rpartition('.')[2])