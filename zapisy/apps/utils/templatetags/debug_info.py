from functools import lru_cache
import subprocess
import sys

import django
from django import template

register = django.template.Library()


def get_line_from_process(process):
    p = subprocess.Popen(process, stdout=subprocess.PIPE)
    outlines = p.stdout.readlines()
    if len(outlines) < 1:
        return ""
    return outlines[0].decode("utf-8")


@register.simple_tag
@lru_cache()
def debug_info():
    """
    A template tag to return debug info:
    Python version and compiler
    Django version
    The latest commit's hash, message, author and date
    Displayed at the bottom of the main page if debug is on
    """
    log_output = get_line_from_process([
        "git", "log", "-n", "1",
        "--pretty=format:%h %s --- %an %ad"
    ])
    branch_name = get_line_from_process([
        "git", "rev-parse", "--abbrev-ref", "HEAD"
    ])
    python_info = f'<p>Python <strong>{sys.version}</strong></p>'
    django_info = f'<p>Django <strong>{django.get_version()}</strong></p>'
    git_info = f'<p>{branch_name} {log_output}</p>'
    return f'{python_info}{django_info}{git_info}'