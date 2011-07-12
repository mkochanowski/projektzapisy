# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Renaming field 'StudentOptions.records_opening_delay_minutes'
        db.rename_column('users_student', 'records_opening_delay_minutes', 'records_opening_bonus_minutes')

    
    def backwards(self, orm):
        
        # Renaming field 'StudentOptions.records_opening_delay_minutes'
        db.rename_column('users_student', 'records_opening_bonus_minutes', 'records_opening_delay_minutes')
