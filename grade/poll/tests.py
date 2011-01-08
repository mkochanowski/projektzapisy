# -*- coding: utf-8 -*-
from django.test              import TestCase
from fereol.grade.poll.models import Section, \
                                     SingleChoiceQuestion, \
                                     MultipleChoiceQuestion, \
                                     OpenQuestion

class SectionTest( TestCase ):
    fixtures = [ 'section_test.json' ]
    
    def setUp( self ):
        self.c_section = Section.objects.get( pk = 1 )
        self.c_ordered = self.c_section.all_questions()
        
    def test_all_questions_gets_only_current_section_questions_1( self ):
        for question in self.c_ordered:
            print dir( question.section )
            self.assertEquals( self.c_section == question.section, True )
    
    def test_all_questions_gets_only_current_section_questions_2( self ):
        for question in self.c_ordered:
            print dir( question.section )
            print question.section.all()
            self.assertEquals( self.c_section == question.section, True )
        
    def test_all_questions_gets_all_current_section_questions( self ):
        pass
    
    def test_all_questions_is_leading_question_first( self ):
        pass

    def test_questions_ordering( self ):
        pass

class PollTest( TestCase ):
    def setUp( self ):
        pass
    
    def test_entitled_student_is_entitled( self ):
        pass
        
    def test_student_without_record_is_not_entitled( self ):
        pass
    
    def test_student_with_wrong_studies_type_is_not_entitled( self ):
        pass

    def test_no_requirements_every_student_entitled( self ):
        pass
        
    def test_sections_ordering( self ):
        pass
        
    def test_get_current_polls_get_only_current_polls( self ):
        pass
        
    def test_get_current_semester_polls_get_only_polls_from_current_semester( self ):
        pass
        
    def test_get_all_polls_for_student_get_only_valid_polls( self ):
        pass
        
    def test_get_all_polls_for_student_get_all_valid_polls( self ):
        pass
