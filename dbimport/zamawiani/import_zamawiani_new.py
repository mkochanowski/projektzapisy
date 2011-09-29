# -*- coding: utf-8 -*-
   
from apps.users.models import Student, StudiaZamawiane
import re
from django.db import transaction

class ImportError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

def import_zamawiani_new(file):
    lines = file.read()
    lines = re.split('\n*', lines)

    for matricula in lines:
        if re.sub('\s','',matricula)=='':
            continue
        if len(matricula)!=6:
            raise ImportError('Niepoprawny indeks długosci rożnej od 6: %s' % (matricula,))
        if re.sub('\d','',matricula)!='':
            raise ImportError('Niepoprawne znaki w indeksie %s' % (matricula,))
             
        try:
            student = Student.objects.get(matricula=matricula)
        except:
            raise ImportError('Brak studenta o indeksie %s' % (matricula,))
        
        try:
            zamawiany = StudiaZamawiane.objects.get_or_create(student=student, defaults={'points':None, 'comments':'', 'bank_account':None})
        except:
            raise ImportError('Problem ze studentem zamawianym o indeksie %s' % (matricula,))
        

@transaction.commit_on_success
def importzamawianinew(data):
    file = data
    import_zamawiani_new(file)