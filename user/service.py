from django.core.exceptions import ValidationError


class UserUpdateService:
    """Service class to handle user profile updates"""

    def __init__(self, validators=None):
        self.validators = validators or {}

    def update_user(self, user, update_data):
        """
        Update user profile with validations

        Args:
            user: The user to be updated
            update_data: Dictionary of fields to update

        Returns:
            Tuple of (success, response)
        """
        for field, new_value in update_data.items():
            if field not in self.validators:
                setattr(user, field, new_value)
                continue

            validator = self.validators[field]
            is_valid, error = validator.validate(user, new_value)

            if not is_valid:
                return False, error

            setattr(user, field, new_value)

        try:
            user.full_clean()
            user.save()
            return True, None
        except ValidationError as e:
            return False, {'detail': e.message_dict}
