# Package Models
There are 22 models that the library will install in your application.

## Workflow

A workflow is the primary model for this feature. All other models in this  
package bear a direct/indirect relationship to this one. The cream of the crop and all that...

### Attributes

| Key           | Type        | Description                                                                           |
|---------------|-------------|---------------------------------------------------------------------------------------|
| id            | UUIDField   | The UUID of the Workflow.                                                             |
| code          | CharField   | An internal code for database level operations.                                       |
| name          | CharField   | The name of the workflow.                                                             |
| version       | PositiveInt | The version of a Workflow. Used to accomodate the <br />evolution of a  Workflow over time. |
| image         | ImageField  | General image associated with the Workflow. (Optional)                                |
| author        | ForeignKey  | The author of the Workflow.                                                           |
| created_by    | ForeignKey  | Administrative user who created the Workflow in the database.                         |
| on_completion | CharField   | What to do once this Workflow has been completed. (Optional)                          |

### Example: Creating a Workflow

    from django.contrib.auth import get_user_model
    from django_workflow_system.models import (
        Workflow, WorkflowAuthor)

    User = get_user_model()
    
    user = User.objects.get(first_name="Eggs", last_name="Benedict", is_staff=True)
    
    # Create a Workflow record.
    workflow = Workflow.objects.create(
        code="42",
        name="Answer to the Ultimate Question of Life, the Universe, and Everything",
        version=1,
        author=WorkflowAuthor.objects.get(user=user),
        created_by=user)

Now what?

## Workflow Author

A WorkflowAuthor is just that, an author of a workflow.

### Attributes

| Key       | Type          | Description                                     |
|-----------|---------------|-------------------------------------------------|
| id        | UUIDField     | The UUID of the WorkflowAuthor.                 |
| user      | OneToOneField | The user associated with the author             |
| title     | CharField     | The title associated with the author            |
| image     | ImageField    | An image associated with the author. (Optional) |
| biography | TextField     | Biography of the author.                        |

### Example: Creating a WorkflowAuthor

    from django.contrib.auth import get_user_model
    from django_workflow_system.models import WorkflowAuthor

    User = get_user_model()
    
    user = User.objects.get(first_name="Eggs", last_name="Benedict", is_staff=True)
    
    # Create a WorkflowAuthor record.
    workflow = WorkflowAuthor.objects.create(
        user=user,
        title="Dr. Eggs Benedict III, Esq.",
        image=open("path/to/eggs_headshot.png", "rb"),
        biography="The man is the third in a distinguished line of eggs.")

## WorkflowCollection

Conceptually, this model exists to provide the ability to group/collect a set of individual Workflows into a sort of "meta-Workflow".

### Attributes

| Key             | Type         | Description                                                                                         |
|-----------------|--------------|-----------------------------------------------------------------------------------------------------|
| id              | UUIDField    | The UUID of the WorkflowCollection.                                                                 |
| code            | CharField    | Code associated with the Workflow Collection.                                                       |
| name            | CharField    | The name of the Workflow Collection                                                                 |
| description     | TextField    | The description of the Workflow Collection.                                                         |
| ordered         | BooleanField | Indicated whether the workflow runs in a certain order.                                             |
| detail_image    | ImageField   | Detail image associated with the collection. (Optional)                                             |
| home_image      | ImageField   | Home image associated with the collection. (Optional)                                               |
| library_image   | ImageField   | Library image associated with the collection. (Optional)                                            |
| version         | PositiveInt  | The version of a Workflow Collection. Used to accommodate<br>the evolution of a Workflow over time. |
| created_by      | ForeignKey   | Administrative user who created the Workflow in the database.                                       |
| assignment_only | BooleanField | If True, the Workflow should only be accessible via assignment.                                     |
| active          | BooleanField | Indication of whether or not the Workflow Collection is <br>currently available for use.            |
| category        | CharType     | The "type" of Workflow.                                                                             |
| metadata        | ManyToMany   | A 'list' of metadata associated to the Collection.                                                  |

### Example: Creating a WorkflowCollection

    from django.contrib.auth import get_user_model
    from django_workflow_system.models import WorkflowCollection

    User = get_user_model()
    
    user = User.objects.get(first_name="Eggs", last_name="Benedict", is_staff=True)
    
    # Create a WorkflowCollection record.
    workflow_collection = WorkflowCollection.objects.create(
        code='42',
        name="Answer to the Ultimate Question of Life, the Universe, and Everything.....the collection",
        description="How many times has this happened to you?",
        ordered=True,
        version=1,
        created_by=user,
        assignment_only=False,
        active=True,
        category="ACTIVITY")

## WorkflowCollectionMember

This model is what allows you to tie Workflows to WorkflowCollections.

### Attributes

| Key                 | Type        | Description                                                |
|---------------------|-------------|------------------------------------------------------------|
| id                  | UUIDField   | The UUID of the WorkflowCollectionMember.                  |
| workflow            | ForeignKey  | The workflow attached to the collection member.            |
| workflow_collection | ForeignKey  | The workflow collection attached to the collection member. |
| order               | PositiveInt | The order of the WorkflowCollectionMember.                 |

### Example: Creating a WorkflowCollectionMember

    from django_workflow_system.models import (
        WorkflowCollection, Workflow, WorkflowCollectionMember)

    workflow = Workflow.objects.get(code="42")
    workflow_collection = WorkflowCollection.objects.get(
        code="42")
    
    workflow_collection_member = WorkflowCollectionMember.objects.create(
        workflow=workflow,
        workflow_collection=worklow_collection,
        order=1)


## WorkflowCollectionEngagement

Used to track user engagement with a Workflow.

### Attributes

| Key                 | Type       | Description                                                                                                                                                                                                                                                                                                                                                                                                                        |
|---------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| id                  | UUIDField  | The UUID of the WorkflowCollectionEngagement.                                                                                                                                                                                                                                                                                                                                                                                      |
| workflow_collection | ForeignKey | The WorkflowCollection object associated with the engagement.                                                                                                                                                                                                                                                                                                                                                                      |
| user                | ForeignKey | The User object who is engaging the Workflow.                                                                                                                                                                                                                                                                                                                                                                                      |
| started             | DateTime   | The start date for the engagement.                                                                                                                                                                                                                                                                                                                                                                                                 |
| finished            | DateTime   | The finish date for the engagement.                                                                                                                                                                                                                                                                                                                                                                                                |
| state               | Dict       | A dictionary with the following key/values:<br><br>    'next_workflow_id': uuid,<br>    'next_step_id': uuid,<br>    'prev_step_id': uuid,<br>    'prev_workflow_id': uuid,<br>    'steps_completed_in_collection': int,<br>    'steps_in_collection': int,<br>    'steps_completed_in_workflow': int,<br>    'steps_in_workflow': int,<br>    'previously_completed_workflows': List[uuid]<br><br>This is computed automatically. |

### Example: Creating a WorkflowCollectionEngagment

    from django.contrib.auth import get_user_model
    from django_workflow_system.models import (
        WorkflowCollection, WorkflowCollectionEngagement)

    User = get_user_model()
    user = User.objects.get(first_name='Eggs')

    workflow_collection = WorkflowCollection.objects.get(
        code='42')
    
    # Note: When creating an engagement, started defaults to the current time
    # and finished defaults to None
    engagement = WorkflowCollectionEngagement.objects.create(
        workflow_collection=workflow_collection,
        user=user)

TODO: ADD MORE ABOUT THE CLASS METHODS HERE

## WorkflowCollectionEngagementDetail

Used to record user engagement with individual steps of a Workflow.

### Attributes

| Key                            | Type       | Description                                                                        |
|--------------------------------|------------|------------------------------------------------------------------------------------|
| id                             | UUIDField  | The UUID of the <br>WorkflowCollectionEngagementDetail.                            |
| workflow_collection_engagement | ForeignKey | The WorkflowCollectionEngagement object <br>associated with the engagement detail. |
| step                           | ForeignKey | The WorkflowStep assosciated with the <br>engagement detail.                       |
| response                       | JSONField  | Internal representation of JSON response <br>from user.                            |
| started                        | DateTime   | The start date of the engagement detail. <br>Defaults to timezone.now()            |
| finished                       | DateTime   | The finish date of the engagement detail.<br>Defaults to None.                     |

### Example: Creating a WorkflowCollectionEngagementDetail

    from django_workflow_system.models import (
        WorkflowCollectionEngagement,
        WorkflowCollectionEngagementDetail)


    