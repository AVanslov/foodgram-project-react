import re

from django.core.exceptions import ValidationError

VALIDATION_SYMBOLS = r'^[\w.@+-]+\z'
VALIDATION_WORD = 'me'


def validate_not_djoser_endpoints(username):
    if username.fullmatch(VALIDATION_WORD):
        raise ValidationError(
            ('Имя пользователя не может начинаться с {}')
            .format(VALIDATION_WORD),
        )


def validate_found_special_symbols(value):
    all_symbols = [i for i in value]
    expected_symbols = re.findall(VALIDATION_SYMBOLS, value)
    unexpected_symbols = list(set(all_symbols) - set(expected_symbols))
    if unexpected_symbols:
        raise ValidationError(
            ('Введены следующие запрещенные символы: {}')
            .format(''.join(set(unexpected_symbols)))
        )


def validate_not_null(value):
    if value == 0:
        raise ValidationError('Количество продукта не может быть равно 0')
