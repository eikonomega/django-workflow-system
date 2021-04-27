from rest_framework import status
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.response import Response


def validate_error_response(response: Response):
    if (
        response.status_code == status.HTTP_404_NOT_FOUND
        and "detail" in response.data
        and isinstance(response.data["detail"], ErrorDetail)
    ):
        return True
    if (
        response.status_code == status.HTTP_403_FORBIDDEN
        and "detail" in response.data
        and isinstance(response.data["detail"], ErrorDetail)
        and response.data["detail"] == "Authentication credentials were not provided."
    ):
        return True

    if (
        response.status_code == status.HTTP_400_BAD_REQUEST
        and "non_field_errors" in response.data
        and isinstance(response.data["non_field_errors"], list)
    ):
        return True

    for field_name in ("email",):
        if (
            response.status_code == status.HTTP_400_BAD_REQUEST
            and "email" in response.data
            and isinstance(response.data[field_name], list)
            and all([isinstance(x, ErrorDetail) for x in response.data[field_name]])
        ):
            return True

    raise ValidationError("did not match any valid schema")
