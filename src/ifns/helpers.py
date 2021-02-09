from django.forms import ValidationError
from django.utils.translation import gettext as _


def validate_code(code):
    if not len(code) == 4:
        raise ValidationError(_('Код ИФНС не соответствует формату'))
