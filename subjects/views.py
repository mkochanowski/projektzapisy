# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from fereol.subjects.models import *

def subjects(self):
    subjects = Subject.objects.all()
    return render_to_response( 'subjects/subjects_list.html', { 'subjects' : subjects } )

def subject( self, slug ):
    subject = Subject.objects.get(slug=slug)
    lectures = Group.objects.filter(subject=subject).filter( type = 1)
    exercises = Group.objects.filter(subject=subject).filter( type = 2 )
    laboratories = Group.objects.filter(subject=subject).filter( type = 3 )
    data = {
            'subject' : subject,
            'lectures' : lectures,
            'exercises' : exercises,
            'laboratories' : laboratories 
    }
                
    return render_to_response( 'subjects/subject.html', data )
