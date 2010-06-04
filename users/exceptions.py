# -*- coding: utf-8 -*-

class NonUserException(Exception):
    '''is thrown when user does not exists'''
    pass

class NonEmployeeException(Exception):
    '''is thrown when employee does not exists'''
    pass