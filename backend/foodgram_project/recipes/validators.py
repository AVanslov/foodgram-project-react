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


def isValidHexaCode(str):
    regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    p = re.compile(regex)
    if (str is None):
        return False
    if (re.search(p, str)):
        return True
    else:
        raise ValidationError(
            'Код цвета должен начинаться с символа # и содержать шесть букв или цифр'
        )
