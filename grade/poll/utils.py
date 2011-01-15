# -*- coding: utf-8 -*- 
from Crypto.PublicKey import RSA

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

def check_signature( ticket, signed_ticket, public_key ):
    #- pk = RSA.importKey( public_key.public_key )
    #- return pk.verify( ticket, (signed_ticket,) )
    return True
