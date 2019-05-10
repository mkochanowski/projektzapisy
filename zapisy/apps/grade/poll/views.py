from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import TemplateView, UpdateView

from apps.enrollment.courses.models.semester import Semester
from apps.grade.ticket_create.models import SigningKey

from .models import Submission
from .forms import TicketsEntryForm, SubmissionEntryForm


def check_grade_status() -> bool:
    active_semesters = Semester.objects.filter(is_grade_active=True).count()
    return active_semesters > 0


class TicketsEntry(TemplateView):
    template_name = "grade/poll/tickets_enter.html"

    def get(self, request):
        form = TicketsEntryForm()
        is_grade_active = check_grade_status()

        return render(
            request,
            self.template_name,
            {"form": form, "is_grade_active": is_grade_active},
        )

    def post(self, request):
        form = TicketsEntryForm(request.POST)
        if form.is_valid():
            tickets = form.cleaned_data["tickets"]
            correct_polls, failed_polls = SigningKey.parse_raw_tickets(tickets)

            submissions = []
            for poll_with_ticket in correct_polls:
                ticket, poll = poll_with_ticket
                submission = Submission.get_or_create(ticket=ticket, poll=poll)
                print(f"Ticket: {ticket}\nPoll: {poll}\nSubmission: {submission}\n")
                submissions.append(submission.pk)

            self.request.session["grade_poll_submissions"] = submissions
            self.request.session["grade_poll_current_submission"] = submissions[0]

        return redirect("grade-poll-v2-submissions")


class SubmissionEntry(UpdateView):
    template_name = "grade/poll/poll_submission.html"
    model = Submission
    slug_field = "submission_slug"
    form_class = SubmissionEntryForm
    jsonfields = []

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        submission = Submission.objects.filter(
            pk=self.request.session["grade_poll_current_submission"]
        ).first()
        if submission:
            kw["jsonfields"] = submission.answers["schema"]

        return kw

    def get_initial(self):
        initial = super().get_initial()
        submission = Submission.objects.filter(
            pk=self.request.session["grade_poll_current_submission"]
        ).first()

        for index, field in enumerate(submission.answers["schema"]):
            field_name = f"field_{index}"
            initial[field_name] = submission.answers["schema"][index]["answer"]

        return initial

    def get_object(self):
        submission = Submission.objects.filter(
            pk=self.request.session["grade_poll_current_submission"]
        ).first()

        return submission

    def get_success_url(self):
        return reverse("grade-poll-v2-submissions")


class PollResults(TemplateView):
    template_name = "grade/poll/poll_results.html"

    def get(self, request):
        is_grade_active = check_grade_status()

        return render(request, self.template_name, {"is_grade_active": is_grade_active})


class SchemasManagement(TemplateView):
    template_name = "grade/poll/poll_schemas.html"

    def get(self, request):
        is_grade_active = check_grade_status()

        return render(request, self.template_name, {"is_grade_active": is_grade_active})


class GradeDetails(TemplateView):
    template_name = "grade/main.html"

    def get(self, request):
        is_grade_active = check_grade_status()

        return render(request, self.template_name, {"is_grade_active": is_grade_active})

