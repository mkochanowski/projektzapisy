from django.core.exceptions import ValidationError

from . import models


def validate_num_required_votes(value):
    max_value = models.ThesesBoardMember.objects.count()
    if not 1 <= value <= max_value:
        raise ValidationError(
            "Liczba wymaganych głosów musi być z przedziału " +
            f'[1, {max_value} (liczba członków komisji)]'
        )
