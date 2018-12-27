from django import template

from apps.users.models import BaseUser
from ..users import wrap_user, is_theses_board_member
from ..models import get_num_ungraded_for_emp


register = template.Library()


@register.simple_tag
def num_ungraded_theses(user):
    """
    Return the number of ungraded theses if the user is a theses board member.
    Returns 0 otherwise, since in that case the template won't show the number.
    """
    if not user.is_authenticated:
        return 0
    wrapped_user = wrap_user(user)
    # FIXME temporary fix for dumb selenium tests where this
    # can happen as they don't create user instances properly
    # To be removed when selenium tests are disabled
    if not isinstance(wrapped_user, BaseUser):
        return 0
    if not is_theses_board_member(wrapped_user):
        return 0
    return get_num_ungraded_for_emp(wrapped_user)
