# -*- coding: utf-8 -*-
   
from apps.users.models import Student, StudiaZamawiane
import re
from django.db import transaction

class ImportError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

def import_zamawiani_info(file):
    i = 1
    lines = file.read()
    lines = re.split('\n*', lines)

    for line in lines:
        if re.sub('\s','',line)=='':
            continue
        line = line.split('|')
        try:
            matricula = line[0]
            points = line[1]
            comments = line[2]
        except:
            raise ImportError('Bledny format danych w lini %s' % (i,))
        
        try:
            student = Student.objects.get(matricula=matricula)
        except:
            raise ImportError('Brak studenta o indeksie %s' % (matricula,))
        
        try:
            zamawiany = StudiaZamawiane.objects.get(student=student)
        except:
            raise ImportError('Brak studenta zamawianego o indeksie %s' % (matricula,))
        
        zamawiany.points = points
        zamawiany.comments = comments
        zamawiany.save()


        i += 1

@transaction.commit_on_success
def importzamawianiinfo(data):
    file = data
    import_zamawiani_info(file)