"""Custom Django admin validators for theses system-related admin pages"""
from django.core.exceptions import ValidationError

from .users import get_num_board_members


def validate_num_required_votes(value):
    """Validate that the numbe of required "accepted" votes
    is in range, that is, not negative and not more than the number
    of theses board members."""
    max_value = get_num_board_members()
    if not 1 <= value <= max_value:
        raise ValidationError(
            "Liczba wymaganych głosów musi być z przedziału " +
            f'[1, {max_value} (liczba członków komisji)]'
        )
