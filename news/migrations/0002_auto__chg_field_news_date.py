# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'News.date'
        db.alter_column('news_news', 'date', self.gf('django.db.models.fields.DateTimeField')())
    
    
    def backwards(self, orm):
        
        # Changing field 'News.date'
        db.alter_column('news_news', 'date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True))
    
    
    models = {
        'news.news': {
            'Meta': {'object_name': 'News'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['news']
