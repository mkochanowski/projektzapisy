# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Message'
        db.create_table('mailer_message', (
            ('message_body', self.gf('django.db.models.fields.TextField')()),
            ('to_address', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('from_address', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('message_body_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('when_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('priority', self.gf('django.db.models.fields.CharField')(default='2', max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('mailer', ['Message'])

        # Adding model 'DontSendEntry'
        db.create_table('mailer_dontsendentry', (
            ('to_address', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('when_added', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('mailer', ['DontSendEntry'])

        # Adding model 'MessageLog'
        db.create_table('mailer_messagelog', (
            ('message_body', self.gf('django.db.models.fields.TextField')()),
            ('to_address', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('from_address', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('when_attempted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('message_body_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('when_added', self.gf('django.db.models.fields.DateTimeField')()),
            ('priority', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('log_message', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('mailer', ['MessageLog'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Message'
        db.delete_table('mailer_message')

        # Deleting model 'DontSendEntry'
        db.delete_table('mailer_dontsendentry')

        # Deleting model 'MessageLog'
        db.delete_table('mailer_messagelog')
    
    
    models = {
        'mailer.dontsendentry': {
            'Meta': {'object_name': 'DontSendEntry'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {})
        },
        'mailer.message': {
            'Meta': {'object_name': 'Message'},
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_body': ('django.db.models.fields.TextField', [], {}),
            'message_body_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'priority': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'mailer.messagelog': {
            'Meta': {'object_name': 'MessageLog'},
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_message': ('django.db.models.fields.TextField', [], {}),
            'message_body': ('django.db.models.fields.TextField', [], {}),
            'message_body_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'priority': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when_added': ('django.db.models.fields.DateTimeField', [], {}),
            'when_attempted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }
    
    complete_apps = ['mailer']
