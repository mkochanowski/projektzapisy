# -*- coding: utf-8 -*-

def getGroups(semester, group = None, type = None, subject = None):
    if subject == -1:
        return {}
    if group:
        return group
    if type:
        if subject:
            groups = Group.objects.filter(type=type, subject=subject)
        else:
            groups = Group.objects.filter(type=type)
    else:
        if subject:
            groups = Group.objects.filter(subject=subject)
        else:
            groups = Group.objects.filter(subject__semester = semester)
            
    
    return groups

def ordering_cmp( ord_1, ord_2 ):
    if str( type( ord_1 )) == \
       "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestionOrdering'>":
        if ord_1.is_leading:
            return -1
            
    if str( type( ord_2 )) == \
       "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestionOrdering'>":
        if ord_2.is_leading:
            return 1
            
    if cmp( ord_1.position, ord_2.position ) == 0:
        if str( type( ord_1 )) == \
           "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestionOrdering'>":
            return -1
        elif str( type( ord_2 )) == \
             "<class 'fereol.grade.poll.models.single_choice_question.SingleChoiceQuestionOrdering'>":
            return 1
        elif str( type( ord_1 )) == \
             "<class 'fereol.grade.poll.models.multiple_choice_question.MultipleChoiceQuestionOrdering'>":
            return -1
        elif str( type( ord_2 )) == \
             "<class 'fereol.grade.poll.models.multiple_choice_question.MultipleChoiceQuestionOrdering'>":
            return 1
        elif str( type( ord_1 )) == \
             "<class 'fereol.grade.poll.models.open_question.OpenQuestionOrdering'>":
            return -1
        else:
            return 1
    else:
        return cmp( ord_1.position, ord_2.position )
