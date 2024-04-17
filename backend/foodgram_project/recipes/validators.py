import re

from django.core.exceptions import ValidationError


def validate_not_djoser_endpoints(username):
    prefixes = ['me', 'reset', 'set', 'resend', 'activation']
    for prefix in prefixes:
        if username.startswith(prefix):
            raise ValidationError(
                ('Имя пользователя не может начинаться с %(prefix)s'),
                params={'prefix': prefix},
            )


def validate_found_special_symbols(value):
    symbols = r'^[\w.@+-]+\z'
    unexpected_symbols = re.findall(symbols, value)
    if unexpected_symbols:
        raise ValidationError(
            ('Введены следующие запрещенные символы: %(unexpected_symbol)s'),
            params={
                str(unexpected_symbol): unexpected_symbol
                for unexpected_symbol in unexpected_symbols
            }
        )
