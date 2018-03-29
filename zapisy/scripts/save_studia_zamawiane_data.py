# -*- coding: utf-8 -*-

from apps.users.models import StudiaZamawiane, StudiaZamawiane2012


def run():
    students_to_save = set()
    for entry in StudiaZamawiane.objects.all():
        students_to_save.add(entry.student_id)
    for entry in StudiaZamawiane2012.objects.all():
        students_to_save.add(entry.student_id)
    with open("zamawiani.txt", "w") as file:
        for student in students_to_save:
            file.write("{}\n".format(student))