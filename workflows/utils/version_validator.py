from django.core.exceptions import ValidationError
from django.db.models import Max


def version_validator(self, model_class):
    """
    Validate a model objects 'version' field.

    self : obj instance
        The instance of the object being validated
    model_class : Class
        Class type of the object being validated
    """
    previous_objects = model_class.objects.filter(code=self.code)
    latest_version = previous_objects.aggregate(Max("version"))["version__max"]
    model_name = model_class.__name__

    # If this is a new code then make sure the version is 1.
    if not latest_version and self.version != 1:
        raise ValidationError(
            {"version": f"Version must be 1 for new {model_name} codes."}
        )

    # If the first and only version of a code is attempting to be updated with a different version
    if (
        previous_objects.count() == 1
        and previous_objects[0].id == self.id
        and self.version != 1
    ):
        raise ValidationError(
            {"version": f"Version must be 1 for the first " f"{model_name} of a code."}
        )

    # Validate that this code's version is not incrementing by more than 1
    if latest_version and self.version > latest_version + 1:
        raise ValidationError(
            {
                "version": f"Version can only be incremented by 1. "
                f"The current latest version of this {model_name} code "
                f"is {latest_version}."
            }
        )
