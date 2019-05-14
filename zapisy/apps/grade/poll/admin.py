from django.contrib import admin

from .models import Poll, Schema, Submission

admin.site.register(Poll)
admin.site.register(Submission)
admin.site.register(Schema)
