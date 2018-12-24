from .utils import wrap_user
from .users import get_user_type, ThesisUserType
from .models import get_num_ungraded_for_emp

invalid_value = {"num_ungraded_thesis": 0}


def num_ungraded_theses(request):
    if not request.user.is_authenticated:
        return invalid_value
    wrapped_user = wrap_user(request.user)
    user_type = get_user_type(wrapped_user)
    if user_type != ThesisUserType.theses_board_member:
        return invalid_value
    return {"num_ungraded_thesis": get_num_ungraded_for_emp(wrapped_user)}
