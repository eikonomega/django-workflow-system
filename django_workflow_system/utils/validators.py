import re

from django.core.exceptions import ValidationError


def validate_code(code):
    """
    Ensure that the code provided follows python_variable_naming_syntax.
    """
    regex = "^[a-z_][a-z0-9_]+$"
    if not re.search(regex, code):
        raise ValidationError("code must be in 'python_variable_naming_syntax'")
