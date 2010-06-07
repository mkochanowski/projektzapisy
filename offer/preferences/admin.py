# -*- coding: utf-8 -*-

"""
    Preferences admin
"""

from django.contrib import admin

from offer.preferences.models import Preference

admin.site.register(Preference)
