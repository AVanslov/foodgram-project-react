from django.core.exceptions import ValidationError


def validate_not_djoser_endpoints(username):
    prefixes = ('me', 'reset', 'set', 'resend', 'activation', )
    if username.startswith(prefixes):
        raise ValidationError(
            ('Имя пользователя не может начинаться с %(username)s'),
            params={"value": username},
        )


def validate_found_special_simbols(value):
    