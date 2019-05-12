from collections import defaultdict, namedtuple
from typing import List
from apps.enrollment.courses.models.semester import Semester
from apps.grade.poll.models import Poll
from apps.users.models import Student

SubmissionWithStatus = namedtuple("SubmissionWithStatus", ["submission", "submitted"])

GroupedSubmissions = namedtuple(
    "GroupedSubmissions",
    ["with_categories", "statuses", "submitted", "total", "progress"],
)


def check_grade_status() -> bool:
    active_semesters = Semester.objects.filter(is_grade_active=True).count()
    return active_semesters > 0


def get_grouped_polls(student: Student) -> (dict, list):
    polls = Poll.get_all_polls_for_student(student)

    courses = {}
    general = []
    for poll in polls:
        if poll.group or poll.course:
            course = poll.group.course if poll.group else poll.course
            if course.id not in courses:
                courses[course.id] = {"courses": course, "polls": []}
            courses[course.id]["polls"].append(poll)
        else:
            general.append(poll)

    return courses, general


def group_submissions(submissions: List[SubmissionWithStatus]) -> (dict, dict):
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
    )
