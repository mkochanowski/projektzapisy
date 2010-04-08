# -*- coding: utf-8 -*-

import datetime
import re

from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.template                import RequestContext

from fereol.records.models          import *
from fereol.subjects.models         import *

@login_required
def subjects(request):
    subjects = Subject.objects.all()
    return render_to_response( 'subjects/subjects_list.html', { 'subjects' : subjects } )

@login_required
def subject( request, slug ):
    subject = Subject.objects.get(slug=slug)
    lectures = Group.objects.filter(subject=subject).filter( type = 1)
    exercises = Group.objects.filter(subject=subject).filter( type = 2 )
    laboratories = Group.objects.filter(subject=subject).filter( type = 3 )

    user_groups = [ g.group.id for g in Record.objects.filter( student = request.user ) ]
    
    for lec in lectures:
        if lec.id in user_groups:
            lec.signed = True
        lec.enrolled = Record.number_of_students(group = lec)

    for exe in exercises:
        if exe.id in user_groups:
            exe.signed = True
        exe.enrolled = Record.number_of_students(group = exe)

    for lab in laboratories:
        if lab.id in user_groups:
            lab.signed = True
        lab.enrolled = Record.number_of_students(group = lab)
    
    data = {
            'subject' : subject,
            'lectures' : lectures,
            'exercises' : exercises,
            'laboratories' : laboratories,
    }         
    return render_to_response( 'subjects/subject.html', data, context_instance = RequestContext( request ) )


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
		
        #@todo: zmienic na ModelForm
		if subjectName and subjectDescription and subjectLectures and subjectExercises and subjectLaboratories:
			subject.name = subjectName
			slug = subjectName.lower()
			#@todo stworzyc funkcje generujaca slug
			slug = re.sub(u'ą', "a", slug)
			slug = re.sub(u'ę', "e", slug)
			slug = re.sub(u'ś', "s", slug)
			slug = re.sub(u'ć', "c", slug)
			slug = re.sub(u'ż', "z", slug)
			slug = re.sub(u'ź', "z", slug)
			slug = re.sub(u'ł', "l", slug)
			slug = re.sub(u'ó', "o", slug)
			slug = re.sub(u'ć', "c", slug)
			slug = re.sub(u'ń', "n", slug)
			slug = re.sub("\W", "-", slug)
			slug = re.sub("-+", "-", slug)
			slug = re.sub("^-", "", slug)
			slug = re.sub("-$", "", slug)
			subject.slug = slug
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
				message = 'Zmiany zostały wprowadzone'
			else:
				message = 'Przedmiot został dodany'
 		else:
			message = 'Wypełnij wszystkie pola'
		
	data = {
		'editMode' : editMode,
		'message' : message,
		'subject' : subject,
	}
	return render_to_response( 'subjects/subject_form.html', data);

@login_required
def subjectHistory( request, slug ):
    subject = Subject.objects.get(slug=slug)
    descriptions = subject.descriptions.order_by('-date')
    data         = {'descriptions' : descriptions}

    return render_to_response ('subjects/subject_history.html', data) 
    
@login_required
def subjectRestore ( request, descid ):
    olddesc = SubjectDescription.objects.get(id = descid)
    
    newdesc             = SubjectDescription()
    newdesc.description = olddesc.description
    newdesc.date        = datetime.datetime.now()
    newdesc.subject     = olddesc.subject
    newdesc.save()
    
    return HttpResponseRedirect(newdesc.subject.slug)
