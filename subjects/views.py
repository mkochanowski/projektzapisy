# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from fereol.subjects.models import *

import datetime

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

def subjectForm(request, sid = None):
	"""
		Formularz do dodawania i edycji przedmiotu.
	"""
	editMode = True if sid else False
	message = None
	
	subject = None
	if editMode:
		try:
			subject = Subject.objects.get(pk = sid)
		except:			
			editMode = False
	
	if request.method == 'POST':
		if not editMode:
			subject = Subject()
	
		subjectName = request.POST.get('name', '')
		subjectDescription = request.POST.get('description', '')
		subjectLectures = request.POST.get('lectures', '')
		subjectExercises = request.POST.get('exercises', '')
		subjectLaboratories = request.POST.get('laboratories', '')
		
		if subjectName and subjectDescription and subjectLectures and subjectExercises and subjectLaboratories:
			subject.name = subjectName
			subject.lectures = subjectLectures
			subject.exercises = subjectExercises
			subject.laboratories = subjectLaboratories
			subject.save()
			
			description = SubjectDescription()
			description.description = subjectDescription
			description.date = datetime.datetime.now()
			description.subject = subject
			description.save()
			
			if editMode:
				message = 'Zmiany zosta³y wprowadzone'
			else:
				message = 'Przedmiot zosta³ dodany'
 		else:
			message = 'Wype³nij wszystkie pola'
		
	data = {
		'editMode' : editMode,
		'message' : message,
		'subject' : subject,
	}
	return render_to_response( 'subjects/subject_form.html', data);