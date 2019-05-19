from collections import defaultdict, namedtuple
from typing import List, Dict

from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models import Poll, Submission
from apps.users.models import Student

SubmissionWithStatus = namedtuple("SubmissionWithStatus", ["submission", "submitted"])

GroupedSubmissions = namedtuple(
    "GroupedSubmissions",
    [
        "with_categories",
        "statuses",
        "submitted",
        "total",
        "progress",
        "progress_numerical",
    ],
)


def check_grade_status() -> bool:
    """Checks whether any of the semesters has grade enabled."""
    active_semesters = Semester.objects.filter(is_grade_active=True).count()

    return active_semesters > 0


def get_grouped_polls(student: Student) -> Dict:
    """Groups polls into a format used by the grade/ticket_create app."""
    polls = Poll.get_all_polls_for_student(student)

    return group_submissions(polls)


def group_submissions_with_statuses(
    submissions: List[SubmissionWithStatus]
) -> (dict, dict):
    """Groups submissions into a structure that is useful for templating.

    Fields are defined in a `GroupedSubmissions` namedtuple.
    """
    grouped_submissions = defaultdict(list)
    submitted_statuses = defaultdict(int)
    submitted_count = 0

    for submission_with_status in submissions:
        submission, status = submission_with_status
        category = submission.category
        if category not in submitted_statuses:
            submitted_statuses[category] = 0
        grouped_submissions[category].append(submission_with_status)
        if status:
            submitted_statuses[category] += 1
            submitted_count += 1

    return GroupedSubmissions(
        with_categories=dict(grouped_submissions),
        statuses=dict(submitted_statuses),
        submitted=submitted_count,
        total=len(submissions),
        progress=f"{submitted_count} / {len(submissions)}",
        progress_numerical=submitted_count / len(submissions),
    )


def group_submissions(submissions: List[Submission]) -> dict:
    """Groups a list of submissions into a dictionary of nested
    categories and subcategories.

    This method is structuring data that allows for easy displaying
    handly tables in views such as the one responsible for summarizing
    the results of students' submissions.
    """
    grouped_submissions = defaultdict(list)

    for submission in submissions:
        category = submission.category
        subcategory = submission.subcategory
        if subcategory not in grouped_submissions[category]:
            grouped_submissions[category].append(subcategory)

    grouped_submissions = dict(sorted(grouped_submissions.items()))

    return grouped_submissions
