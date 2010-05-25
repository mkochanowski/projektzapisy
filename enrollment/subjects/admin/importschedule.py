# -*- coding: utf-8 -*-

from django.db import transaction
from django.template.defaultfilters import slugify
from lxml import etree
from fereol.enrollment.subjects.models import Semester, Group, Subject, Term,\
     SubjectEntity, Type, Classroom
from fereol.users.models import Employee

XSCHEMA = 'enrollment/subjects/admin/xml/semesterschedule.xsd'

@transaction.commit_on_success
def import_semester_schedule(xmlfile):
    def get_teacher(el_teacher):
        name = el_teacher.find('name').text
        surname = el_teacher.find('surname').text

        try:
            employee = Employee.objects.get(first_name=name,
                                        last_name=surname
                                        )
        except Employee.DoesNotExist:
            raise Employee.DoesNotExist('Employee name="%s"  surname="%s" does not exist' % (name, surname))

        return employee
    
    def get_teachers(el_teachers):
        teachers = []
        
        for el_teacher in el_teachers:
            teachers.append(get_teacher(el_teacher))
            
        return teachers
    
    def create_subject(el_subject, semester):
        teachers = get_teachers(element.find('teachers'))

        name = el_subject.find('name').text
        entity = SubjectEntity.objects.get_or_create(name=name)[0]
        slug = slugify(semester.year + '_' + name)
        type = Type.objects.get_or_create(name=el_subject.find('type').text)[0]
        desc = el_subject.find('desc').text
        lectures = el_subject.find('lectures').text
        exercises = el_subject.find('exercises').text
        labs = el_subject.find('laboratories').text

        subject = Subject.objects.create(entity=entity,
                                         name=name,
                                         slug=slug,
                                         semester=semester,
                                         type=type,
                                         description=desc,
                                         lectures=lectures,
                                         exercises=exercises,
                                         laboratories=labs
                                         )
        
        subject.teachers = teachers
        subject.save()

        create_groups(element.find('groups'), subject)
        
    def create_groups(el_groups, subject):
        for el_group in el_groups:
            el_teacher = el_group.find('teacher')

            if el_teacher:
                teacher = get_teacher(el_teacher)
            else:
                teacher = None

            el_type_text = el_group.find('type').text

            if el_type_text == 'lecture':
                type = '1'
            elif el_type_text == 'exercise':
                type = '2'
            elif el_type_text == 'laboratory':
                type = '3'

            limit = el_group.find('limit').text

            group = Group.objects.create(subject=subject,
                         teacher=teacher,
                         type=type,
                         limit=limit
                         )
                         
            create_terms(el_group.find('terms'), group)


    def create_terms(el_terms, group):
        terms = []
        
        for el_term in el_terms:
            el_day_text = el_term.find('day').text

            if(el_day_text == 'monday'):
                day = '1'
            elif(el_day_text == 'tuesday'):
                day = '2'
            elif(el_day_text == 'wednesday'):
                day = '3'
            elif(el_day_text == 'thursday'):
                day = '4'
            elif(el_day_text == 'friday'):
                day = '5'
            elif(el_day_text == 'saturday'):
                day = '6'
            elif(el_day_text == 'sunday'):
                day = '7'

            start_time = el_term.find('startTime').text
            end_time = el_term.find('endTime').text
            classroom = Classroom.objects.get_or_create(number=el_term.find('room').text
                                                        )[0]

            terms.append(Term.objects.create(dayOfWeek=day,
									         start_time=start_time,
									         end_time=end_time,
									         classroom=classroom,
									         group=group
									         )
                         )

        return terms
    
    schema = etree.XMLSchema(file=XSCHEMA)
    events = etree.iterparse(xmlfile,
                             remove_blank_text=True,
                             remove_comments=True,
                             events=('start','end'),
                             schema=schema
                             )

    new_sem = False

    for event, element in events:
        if event == 'start' and element.tag == 'semester':
            new_sem = True
        elif new_sem == True and event == 'end' and element.tag == 'year':
            sem_year = element.text
        elif new_sem == True and event == 'end' and element.tag == 'type':
            if element.text == 'winter':
                sem_type = Semester.TYPE_WINTER
            elif element.text == 'summer':
                sem_type = Semester.TYPE_SUMMER

            new_sem = False

            semester = Semester.objects.create(visible=False,
                                               year=sem_year,
                                               type=sem_type)

        elif event == 'end' and element.tag == 'subject':
            create_subject(element, semester)
            element.clear()

            while element.getprevious() is not None:
                del element.getparent()[0]


