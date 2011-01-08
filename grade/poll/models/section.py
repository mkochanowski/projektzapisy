# -*- coding: utf8 -*-
from sys       import maxint
from django.db import models

from open_question            import OpenQuestionOrdering
from single_choice_question   import SingleChoiceQuestionOrdering
from multiple_choice_question import MultipleChoiceQuestionOrdering
                        
class Section( models.Model ):
    title       = models.CharField( max_length = 50,  verbose_name = 'tytuł' )
    description = models.TextField( blank = True, verbose_name = 'opis' ) 
    poll        = models.ManyToManyField( 'Poll', verbose_name = 'ankieta',
                                          through = 'SectionOrdering' )
    
    class Meta:
        verbose_name        = 'sekcja'
        verbose_name_plural = 'sekcje'
        app_label           = 'poll'
        
    def __unicode__( self ):
        return unicode( self.title )
        
    def all_questions( self ):
        open            = OpenQuestionOrdering.objects.filter( section = self )
        single_choice   = SingleChoiceQuestionOrdering.objects.filter( section = self )
        multiple_choice = MultipleChoiceQuestionOrdering.objects.filter( section = self )
        
        questions = []
        
        open_ind = single_ind = multi_ind = 0
        
        try:
            if single_choice[0].is_leading:
                single_ind = 1
                questions.append( single_choice[0] )
        except:
            pass
        
        max_ = max( len( open ), len( single_choice ), len( multiple_choice ))
        
        while ( open_ind < max_ and single_ind <= max_ and multi_ind <= max_ ) or \
              ( open_ind <= max_ and single_ind < max_ and multi_ind <= max_ ) or \
              ( open_ind <= max_ and single_ind <= max_ and multi_ind < max_ ):
                  
            try:
                sc  = single_choice[ single_ind ]
                scp = sc.position
            except:
                scp = maxint
            
            try:
                mc  = multiple_choice[ multi_ind ]
                mcp = mc.position
            except:
                mcp = maxint
                
            try:
                o   = open[ open_ind ]
                op  = o.position
            except:
                op  = maxint
            
            if min( op, mcp, scp ) == scp:
                questions.append( sc.question )
                single_ind += 1
            elif min( op, mcp, scp ) == mcp:
                questions.append( mc.question )
                multi_ind += 1
            else:
                questions.append( o.question )
                open_ind += 1
        return questions
        
class SectionOrdering( models.Model ):
    poll     = models.ForeignKey( 'Poll',      verbose_name = 'ankieta' )
    section  = models.ForeignKey( Section, verbose_name = 'sekcja' )
    position = models.IntegerField( verbose_name = 'pozycja' )

    class Meta:
        verbose_name_plural = 'pozycje sekcji'
        verbose_name        = 'pozycja sekcji'
        ordering            = [ 'poll', 'position' ]
        unique_together     = [ 'poll', 'position' ]
        app_label           = 'poll'
        
    def __unicode__( self ):
        return unicode( self.position ) + u'[' + unicode( self.poll ) + u']' + unicode( self.section )
