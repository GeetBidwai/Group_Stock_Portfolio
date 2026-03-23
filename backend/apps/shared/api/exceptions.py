from rest_framework import status
from rest_framework.exceptions import APIException


class FeatureDisabledException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "This feature is disabled."
    default_code = "feature_disabled"


class DomainValidationException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The request could not be processed."
    default_code = "domain_validation_error"
