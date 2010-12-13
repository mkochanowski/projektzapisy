# -*- coding: utf-8 -*-

from django.contrib import admin
from grade.cryptography.models import *

admin.site.register(GroupsConnection)
admin.site.register(PublicKey)
admin.site.register(PrivateKey)
