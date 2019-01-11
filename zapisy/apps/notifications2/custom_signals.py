import django.dispatch

student_pulled = django.dispatch.Signal(providing_args=['instance', 'user'])
teacher_changed = django.dispatch.Signal(providing_args=['instance', 'teacher'])
