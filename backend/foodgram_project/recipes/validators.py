import re

from django.core.exceptions import ValidationError

VALIDATION_SYMBOLS = r'[^\w.@+-]'
VALIDATION_WORD = 'me'


def validate_not_djoser_endpoints(username):
    if username == VALIDATION_WORD:
        raise ValidationError(
            ('Имя пользователя не может быть: {}')
            .format(VALIDATION_WORD),
        )


def validate_found_special_symbols(value):
    unexpected_symbols = re.findall(VALIDATION_SYMBOLS, value)
    if unexpected_symbols:
        raise ValidationError(
            ('Введены следующие запрещенные символы: {}')
            .format(''.join(set(unexpected_symbols)))
        )
