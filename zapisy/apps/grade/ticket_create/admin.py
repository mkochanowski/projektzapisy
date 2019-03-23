from django.contrib import admin
from apps.grade.ticket_create.models import SigningKey, StudentGraded


class StudentGradedAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester')
    search_fields = ('student__user__first_name',
                     'student__user__last_name',
                     'student__matricula',)

    list_filter = ('semester',)

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        qs = super(StudentGradedAdmin, self).get_queryset(request)
        return qs.select_related('semester', 'student', 'student__user')


class SigningKeyAdmin(admin.ModelAdmin):

    list_display = ('poll', )
    search_fields = ('poll__title',)


admin.site.register(SigningKey, SigningKeyAdmin)
admin.site.register(StudentGraded, StudentGradedAdmin)
