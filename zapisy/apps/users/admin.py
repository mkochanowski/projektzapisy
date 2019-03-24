from django.http import HttpResponse, HttpRequest
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django import forms
import django.forms.models
from django.contrib.auth import admin as django_auth_admin
from django.db.models import QuerySet
import csv

from apps.users.models import (
    Employee,
    Student,
    Program)
from apps.enrollment.courses.models.semester import Semester
from apps.enrollment.records.models import Record


class ExtendedUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    fieldsets = [
        (None, {'fields': ('username', 'password')}),
        ('Dane osobowe', {'fields': ('first_name', 'last_name', 'email')}),
        ('Dodatkowe dane', {'fields': ('is_student', 'is_employee')}),
        ('Uprawnienia', {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        ('Ważne daty', {'fields': ('last_login', 'date_joined')}),
        ('Grupy', {'fields': ('groups',)})
    ]
    list_filter = ('is_staff', 'is_superuser', 'is_student', 'is_employee')
    search_fields = ('username', 'first_name', 'last_name', 'email')


def export_as_csv(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> HttpResponse:
    semester = Semester.get_current_semester()

    records = Record.objects.filter(
        student__in=queryset,
        group__course__semester=semester,
        status=1).select_related(
        'student',
        'student__user',
        'group',
        'group__course')

    opts = modeladmin.model._meta

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')

    writer = csv.writer(response)
    for record in records:
        writer.writerow([record.student.matricula,
                         record.student.user.first_name,
                         record.student.user.last_name,
                         record.group.course.name,
                         record.group.get_type_display(),
                         record.group.get_terms_as_string()])
    return response


export_as_csv.short_description = "Export jako CSV"


class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'get_full_name', 'ects', 'get_type_of_studies')
    fieldsets = [
        (None, {'fields': ['user', 'matricula', 'status']}),
        ('Studia', {'fields': ['numeryczna_l', 'dyskretna_l', 'program', 'semestr', 'ects']}),
        ('Zapisy', {'fields': ['records_opening_bonus_minutes', 'block']}),
        ('Inne', {'fields': ['receive_mass_mail_enrollment', 'receive_mass_mail_offer', 'receive_mass_mail_grade', 'last_news_view'], 'classes': ['collapse']}),
    ]
    search_fields = ('user__first_name', 'user__last_name', 'matricula')
    list_filter = ('program', 'status', 'semestr')
    ordering = ['user__last_name', 'user__first_name']
    list_display_links = ('get_full_name',)
    list_max_show_all = 9999

    actions = [export_as_csv]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super(StudentAdmin, self).get_queryset(request)
        return qs.select_related('program', 'program__type_of_points', 'user')


class ProgramAdmin(admin.ModelAdmin):

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super(ProgramAdmin, self).get_queryset(request)
        return qs.select_related('type_of_points')


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'homepage', 'room', 'consultations',)
    list_filter = ('status',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    fieldsets = [
        (None, {
            'fields': [
                'user', 'status', 'homepage', 'room', 'consultations']}), ('Ogłoszenia mailowe', {
                    'fields': [
                        'receive_mass_mail_enrollment', 'receive_mass_mail_offer'], 'classes': ['collapse']}), ]
    ordering = ['user__last_name', 'user__first_name']
    list_display_links = ('get_full_name',)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super(EmployeeAdmin, self).get_queryset(request)
        return qs.select_related('user')


class StudentInline(admin.StackedInline):
    model = Student
    extra = 0
    max_num = 1


class EmployeeInline(admin.StackedInline):
    model = Employee
    extra = 0
    max_num = 1


class UserAdmin(django_auth_admin.UserAdmin):
    def show_user_groups(self, user: User):
        """Django requires that all fields are model attributes or admin callables,
        so we need this extra method
        """
        return ', '.join(group.name for group in user.groups.all())
    show_user_groups.short_description = 'Grupy'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('groups')

    inlines = [StudentInline, EmployeeInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'show_user_groups')
    list_filter = ('is_active', 'is_staff')


class GroupUsersChoiceField(forms.ModelMultipleChoiceField):
    """A simple subclass of Django's standard ModelMultipleChoiceField
    that additionally formats users as both their full names and logins,
    if the full name is defined; otherwise we return just the login
    """
    def label_from_instance(self, obj: User):
        full_name = obj.get_full_name()
        return f'{full_name} ({obj.username})' if full_name else obj.username


class GroupAdminForm(forms.ModelForm):
    """ModelForm that adds an additional multiple select field for managing
    the users in the group.
    """
    users = GroupUsersChoiceField(
        User.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Users', False),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            initial_users = self.instance.user_set.values_list('pk', flat=True)
            self.initial['users'] = initial_users

    def save(self, *args, **kwargs):
        # Set commit to true so that the model corresponding to this form is definitely
        # created and saved in the DB, which lets use use many-to-many relationships
        # immediately (in particular, the users in this group)
        # See https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method
        # If commit is ever False, Django will overwrite save_m2m with its own method;
        # we don't want that to happen, as our custom logic would never be triggered
        # See BaseModelForm.save() in Django sources
        kwargs['commit'] = True
        return super(GroupAdminForm, self).save(*args, **kwargs)

    def save_m2m(self):
        # Populate the model instance with the users from the admin form widget
        self.instance.user_set.set(self.cleaned_data['users'])


class GroupAdmin(django_auth_admin.GroupAdmin):
    """Customized GroupAdmin class that uses the customized form to allow
    management of users within a group.
    """
    form = GroupAdminForm


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Program, ProgramAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
