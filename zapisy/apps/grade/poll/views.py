import itertools
from collections import namedtuple
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import TemplateView, UpdateView, View

from apps.enrollment.courses.models.semester import Semester
from apps.grade.ticket_create.models import SigningKey
from apps.grade.poll.utils import (
    check_grade_status,
    group_submissions,
    SubmissionWithStatus,
)

from .models import Submission
from .forms import TicketsEntryForm, SubmissionEntryForm


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

            entries = []
            for poll_with_ticket_id in correct_polls:
                submission = Submission.get_or_create(poll_with_ticket_id)
                entry = SubmissionWithStatus(
                    submission=submission, submitted=submission.submitted
                )
                entries.append(entry)

            self.request.session["grade_poll_submissions"] = entries

        return redirect("grade-poll-submissions")


class SubmissionEntry(UpdateView):
    template_name = "grade/poll/submission.html"
    model = Submission
    slug_field = "submissions"
    form_class = SubmissionEntryForm

    def get(self, *args, **kwargs):
        if "grade_poll_submissions" in self.request.session:
            return super(SubmissionEntry, self).get(*args, **kwargs)
        return redirect("grade-poll-tickets-enter")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_grade_active"] = check_grade_status()
        context["active_submission"] = self.active_submission
        context["current_index"] = self.current_index
        # grouped_submissions, grouped_statuses = group_submissions(self.submissions)
        context["grouped_submissions"] = group_submissions(self.submissions)
        # context["grouped_submissions"] = dict(grouped_submissions)
        # context["grouped_statuses"] = dict(grouped_statuses)
        context["iterator"] = itertools.count()

        return context

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        submission = self.active_submission
        if submission:
            kw["jsonfields"] = submission.answers["schema"]

        return kw

    def get_initial(self):
        initial = super().get_initial()
        submission = self.active_submission

        for index, field in enumerate(submission.answers["schema"]):
            field_name = f"field_{index}"
            initial[field_name] = submission.answers["schema"][index]["answer"]

        return initial

    @property
    def active_submission(self):
        submission_pk = self.submissions[
            self.current_index % len(self.submissions)
        ].submission.pk

        submission = Submission.objects.filter(pk=submission_pk).first()

        return submission

    @property
    def submissions(self):
        return self.request.session["grade_poll_submissions"]

    @property
    def current_index(self):
        return int(self.kwargs["submission_index"])

    def get_object(self):
        return self.active_submission

    def get_success_url(self):
        submissions = self.submissions
        submissions[self.current_index] = SubmissionWithStatus(
            submission=self.active_submission, submitted=True
        )
        self.request.session["grade_poll_submissions"] = submissions
        print(f"Current index: {self.current_index}")
        next_index = 0

        for index in range(
            self.current_index + 1, len(submissions) + self.current_index + 1
        ):
            print("Searching for not submitted poll, index:", index)
            mod_index = index % len(submissions)
            if not submissions[mod_index].submitted:
                next_index = mod_index
                print(f"Found {mod_index}!")
                break

        return reverse(
            "grade-poll-submissions", kwargs={"submission_index": next_index}
        )


class PollResults(TemplateView):
    template_name = "grade/poll/results.html"

    def get(self, request):
        is_grade_active = check_grade_status()

        return render(request, self.template_name, {"is_grade_active": is_grade_active})


class GradeDetails(TemplateView):
    template_name = "grade/main.html"

    def get(self, request):
        is_grade_active = check_grade_status()

        return render(request, self.template_name, {"is_grade_active": is_grade_active})


class ClearSession(View):
    def get(self, request):
        del self.request.session["grade_poll_submissions"]
        return redirect("grade-poll-tickets-enter")
