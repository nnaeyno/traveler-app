from abc import ABC, abstractmethod
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class UserUpdateValidator(ABC):
    """Abstract base class for user update validations"""

    @abstractmethod
    def validate(self, user, new_value):
        """Validate a specific user attribute"""
        pass


class UniqueFieldValidator(UserUpdateValidator):
    """Validator to ensure a field is unique across users"""

    def __init__(self, field_name, error_message):
        self.field_name = field_name
        self.error_message = error_message

    def validate(self, user, new_value):
        """
        Check if the new value is unique across all users
        excluding the current user
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if User.objects.exclude(pk=user.pk).filter(**{self.field_name: new_value}).exists():
            return False, {self.field_name: self.error_message}
        return True, None


class PasswordValidator(UserUpdateValidator):
    """Validator for password updates"""

    def validate(self, user, new_password):
        """
        Validate password against Django's password validation
        """
        try:
            validate_password(new_password, user)
            return True, None
        except ValidationError as e:
            return False, {'password': list(e.messages)}

