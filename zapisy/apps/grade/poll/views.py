from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, UpdateView

from apps.enrollment.courses.models.semester import Semester

from .models import Submission
from .forms import TicketsEntryForm, SubmissionEntryForm


def check_grade_status() -> bool:
    active_semesters = Semester.objects.filter(is_grade_active=True).count()
    return active_semesters > 0


class TicketsEntry(TemplateView):
    template_name = "grade/poll_v2/tickets_enter.html"

    def get(self, request):
        form = TicketsEntryForm()
        is_grade_active = check_grade_status()

        return render(
            request,
            self.template_name,
            {"form": form, "is_grade_active": is_grade_active},
        )

    def post(self, request):
        return redirect("grade-poll-v2-submissions")


class SubmissionEntry(UpdateView):
    template_name = "grade/poll_v2/poll_submission.html"
    model = Submission
    slug_field = "submission_slug"
    form_class = SubmissionEntryForm
    jsonfields = [
        {"name": "First Name", "slug": "first_name"},
        {"name": "Last Name", "slug": "last_name"},
    ]

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["jsonfields"] = self.jsonfields
        return kw

    def get_initial(self):
        initial = super().get_initial()
        for field in self.jsonfields:
            initial[field["slug"]] = self.object.fields.get(field["slug"])
        return initial

    def get_object(self):
        return get_object_or_404(
            # Submission, pk=request.session["poll_v2_submission_id"]
            Submission,
            pk=1,
        )


class PollResults(TemplateView):
    template_name = "grade/poll_v2/poll_results.html"

    def get(self, request):
        is_grade_active = check_grade_status()

        return render(request, self.template_name, {"is_grade_active": is_grade_active})


class SchemasManagement(TemplateView):
    template_name = "grade/poll_v2/poll_schemas.html"

    def get(self, request):
        is_grade_active = check_grade_status()

        return render(request, self.template_name, {"is_grade_active": is_grade_active})


class GradeDetails(TemplateView):
    template_name = "grade/main.html"

    def get(self, request):
        is_grade_active = check_grade_status()

        return render(request, self.template_name, {"is_grade_active": is_grade_active})


# class SubmissionEntry(TemplateView):
#     template_name = "grade/poll_v2/poll_submission.html"

#     def get(self, request):
#         form = SubmissionEntryForm()
#         return render(request, self.template_name, {"form": form})

#     def post(self, request):
#         return render(request, self.template_name)
