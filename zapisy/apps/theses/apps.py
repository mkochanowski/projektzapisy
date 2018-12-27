from django.apps import AppConfig
from django.db.models import Lookup
from django.db.models.fields import Field


class NotEqual(Lookup):
    """
    A custom lookup allowing "not equal" conditions in queryset filters
    Taken from https://docs.djangoproject.com/en/2.1/howto/custom-lookups/#a-simple-lookup-example
    This is a contentious issue in Django, see https://code.djangoproject.com/ticket/5763
    The obvious alternative is to use Q objects, but Q object negation (~)
    doesn't work the way we want with many-to-many (list) value searching;
    ~Q(votes__value=1) is not the same as votes__value__ne=1;
    the former means "The list (votes) does not contain a value of 1" whereas the latter
    means "The list contains a value that is not 1"
    To see how this is used, check filter_ungraded_for_emp in models.py
    """

    lookup_name = 'ne'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params


class ThesesAppConfig(AppConfig):
    name = 'apps.theses'

    def ready(self):
        Field.register_lookup(NotEqual)
