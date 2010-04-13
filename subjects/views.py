# -*- coding: utf-8 -*-

import datetime
import re

from django.contrib.auth.decorators import login_required
from django.http                    import HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.shortcuts               import redirect

from fereol.records.models          import *
from fereol.subjects.models         import *

@login_required
def subjects(request):
    subjects = Subject.objects.all()
    return render_to_response( 'subjects/subjects_list.html', { 'subjects' : subjects, 'mode' : 'list' }, context_instance = RequestContext(request) )

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
            'subject'       : subject,
            'lectures'      : lectures,
            'exercises'     : exercises,
            'laboratories'  : laboratories,
            'mode'          : 'details',
            'subjects'      : Subject.objects.all()             
    }         
    return render_to_response( 'subjects/subjects_list.html', data, context_instance = RequestContext( request ) )


def subjectForm(request, sid = None):
    """
        Formularz do dodawania i edycji przedmiotu.
    """
    editMode = True if sid else False    
    message = None
    booksToForm = []
    success = False
    subjectDescription = ""
    
    subject = None
    if editMode:
        try:
            subject = Subject.objects.get(pk = sid)
            subjectDescription = subject.description().description 
        except:            
            editMode = False
    
    if request.method == 'POST':        
        if not editMode:
            subject = Subject()
            
        correctForm = True
        
        """ Read data from html form """
        
        subjectName = request.POST.get('name', '')
        subjectDescription = request.POST.get('description', '')
        
        books = request.POST.getlist('books[]')
        
        try:
            subjectLectures = int(request.POST.get('lectures', 0))                        
        except:        
            subjectLectures = 0             
            
        try:            
            subjectExercises = int(request.POST.get('exercises', 0))            
        except:                    
            subjectExercises = 0            
            
        try:            
            subjectLaboratories = int(request.POST.get('laboratories', 0))
        except:                    
            subjectLaboratories = 0
            
        subject.name = subjectName
        subject.lectures = subjectLectures
        subject.exercises = subjectExercises
        subject.laboratories = subjectLaboratories            
        subject.slug = subject.createSlug(subject.name)        
        
        if Subject.objects.filter(slug = subject.slug).exclude(id = subject.id).count() > 0:                
            message = 'Istnieje już przedmiot o takiej nazwie'
            correctForm = False                                    
            
        if subjectName == "" or subjectDescription == "":
            message = 'Wypełnij wszystkie pola'
            correctForm = False
                            
        if subjectLectures < 0 and subjectExercises < 0 and subjectLaboratories < 0:
            message = "Ilości godzin muszą być liczbami naturalnymi"
            correctForm = False
            
        if correctForm:
                        
            subject.save()
            
            description = SubjectDescription()
            description.description = subjectDescription
            description.date = datetime.datetime.now()
            description.subject = subject
            description.save()
            
            for book in subject.books.all():
                fieldValue =  request.POST.get('book' + str(book.id), None)                                                
                if fieldValue != None:
                    if fieldValue == "":                    
                        book.delete()
                    elif book.name != fieldValue:
                        book.name = fieldValue
                        book.save()                                                
          
            for bookName in books:
                if bookName != "":
                    book = Book(name = bookName, subject = subject).save()
                    
            success = True                                     
                                               
            if editMode:
                message = 'Zmiany zostały wprowadzone'
            else:
                message = 'Przedmiot został dodany'
                subject = None
                subjectDescription = ""
        
    if subject and subject.id:
        booksToForm = list(subject.books.all())
        
        
    if request.method == "POST" and not success:
        for bookName in request.POST.getlist('books[]'):
            booksToForm.append({ "id" : None, "name" : bookName})
    
    
    data = {
        'editForm'  : True,
        'editMode'  : editMode,
        'message'   : message,
        'subject'   : subject,
        'books'     : booksToForm,
        'subjectDescription' : subjectDescription,
        'mode'      : 'form',
        'subjects'  : Subject.objects.all()
    }
    return render_to_response( 'subjects/subjects_list.html', data, context_instance = RequestContext(request));

@login_required
def subjectHistory( request, sid ):
    subject      = Subject.objects.get( pk = sid)
    descriptions = subject.descriptions.order_by( '-date' )
    data         = { 'descriptions' : descriptions }
    
    return render_to_response ('subjects/subject_history.html', data, context_instance = RequestContext(request)) 
    
@login_required
def subjectViewArcival( request, descid ):
    desc = SubjectDescription.objects.get( pk = descid )
    data = {'desc' : desc}
    
    return render_to_response ('subjects/subject_archival.html', data)
    
@login_required
def subjectRestore ( request, descid ):
    olddesc = SubjectDescription.objects.get( pk = descid )
    newdesc             = SubjectDescription()
    newdesc.description = olddesc.description
    newdesc.date        = datetime.datetime.now()
    newdesc.subject     = olddesc.subject
    newdesc.save()
    
    return subject( request, olddesc.subject.slug )
