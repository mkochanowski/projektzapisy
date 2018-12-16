from . import models


def _get_settings():
    return models.ThesesSystemSettings.objects.get()


def get_num_required_votes():
    return _get_settings().num_required_votes
