# -*- coding: utf-8 -*-

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import update_wrapper

from users.models import Employee, Student

def student_required(function=None,
                     redirect_to=None):
    """
    Decorator that checks that the user has a student profile,
    redirecting or returning http 403 forbidden as needed.
    """
    def test_f(user):
        try:
            user.student
            return True
        except AttributeError:
            return False
        except Student.DoesNotExist:
            return False
    if function:
        return _CheckProfileOr403(function, test_f, redirect_to)
    return (lambda f: _CheckProfileOr403(f, test_f, redirect_to))

def employee_required(function=None,
                      redirect_to=None):
    """
    Decorator that checks that the user has a student profile,
    redirecting or returning http 403 forbidden as needed.
    """
    def test_f(user):
        try:
            user.employee
            return True
        except AttributeError:
            return False
        except Student.DoesNotExist:
            return False
    if function:
        return _CheckProfileOr403(function, test_f, redirect_to)
    return lambda f: _CheckProfileOr403(f, test_f, redirect_to)

class _CheckProfileOr403(object):
    """
    Class that checks that the user passes the given test,
    redirecting to the given view or returning 403 if necessary.

    Check django.contrib.auth.decorators._CheckLogin for more info.
    """
    def __init__(self, view_func, test_func, redirect_to=None):
        self.view_func = view_func
        self.test_func = test_func
        self.redirect_to = redirect_to
        # see _CheckLogin
        update_wrapper(self, view_func, updated=())
        for k in view_func.__dict__:
            if k not in self.__dict__:
                self.__dict__[k] = view_func.__dict__[k]
    
    def __get__(self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return _CheckProfileOr403(view_func, self.test_func, self.redirect_to)
    
    def __call__(self, request, *args, **kwargs):
        if self.test_func(request.user):
            return self.view_func(request, *args, **kwargs)
        if self.redirect_to:
            return redirect(self.redirect_to)
        return HttpResponseForbidden("You do not have a required profile") # TODO - error page
