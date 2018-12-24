from django import template
from ..utils import wrap_user
from ..users import get_user_type, ThesisUserType
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
    user_type = get_user_type(wrapped_user)
    if user_type != ThesisUserType.theses_board_member:
        return 0
    return get_num_ungraded_for_emp(wrapped_user)
