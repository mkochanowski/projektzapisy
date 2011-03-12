# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Option'
        db.create_table('poll_option', (
            ('content', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['Option'])

        # Adding model 'Section'
        db.create_table('poll_section', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('poll', ['Section'])

        # Adding model 'MultipleChoiceQuestion'
        db.create_table('poll_multiplechoicequestion', (
            ('content', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('choice_limit', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('has_other', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('poll', ['MultipleChoiceQuestion'])

        # Adding M2M table for field section on 'MultipleChoiceQuestion'
        db.create_table('poll_multiplechoicequestion_section', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multiplechoicequestion', models.ForeignKey(orm['poll.multiplechoicequestion'], null=False)),
            ('section', models.ForeignKey(orm['poll.section'], null=False))
        ))
        db.create_unique('poll_multiplechoicequestion_section', ['multiplechoicequestion_id', 'section_id'])

        # Adding M2M table for field options on 'MultipleChoiceQuestion'
        db.create_table('poll_multiplechoicequestion_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multiplechoicequestion', models.ForeignKey(orm['poll.multiplechoicequestion'], null=False)),
            ('option', models.ForeignKey(orm['poll.option'], null=False))
        ))
        db.create_unique('poll_multiplechoicequestion_options', ['multiplechoicequestion_id', 'option_id'])

        # Adding model 'SingleChoiceQuestion'
        db.create_table('poll_singlechoicequestion', (
            ('content', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('is_scale', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['SingleChoiceQuestion'])

        # Adding M2M table for field section on 'SingleChoiceQuestion'
        db.create_table('poll_singlechoicequestion_section', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('singlechoicequestion', models.ForeignKey(orm['poll.singlechoicequestion'], null=False)),
            ('section', models.ForeignKey(orm['poll.section'], null=False))
        ))
        db.create_unique('poll_singlechoicequestion_section', ['singlechoicequestion_id', 'section_id'])

        # Adding M2M table for field options on 'SingleChoiceQuestion'
        db.create_table('poll_singlechoicequestion_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('singlechoicequestion', models.ForeignKey(orm['poll.singlechoicequestion'], null=False)),
            ('option', models.ForeignKey(orm['poll.option'], null=False))
        ))
        db.create_unique('poll_singlechoicequestion_options', ['singlechoicequestion_id', 'option_id'])

        # Adding model 'OpenQuestion'
        db.create_table('poll_openquestion', (
            ('content', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['OpenQuestion'])

        # Adding M2M table for field section on 'OpenQuestion'
        db.create_table('poll_openquestion_section', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('openquestion', models.ForeignKey(orm['poll.openquestion'], null=False)),
            ('section', models.ForeignKey(orm['poll.section'], null=False))
        ))
        db.create_unique('poll_openquestion_section', ['openquestion_id', 'section_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Option'
        db.delete_table('poll_option')

        # Deleting model 'Section'
        db.delete_table('poll_section')

        # Deleting model 'MultipleChoiceQuestion'
        db.delete_table('poll_multiplechoicequestion')

        # Removing M2M table for field section on 'MultipleChoiceQuestion'
        db.delete_table('poll_multiplechoicequestion_section')

        # Removing M2M table for field options on 'MultipleChoiceQuestion'
        db.delete_table('poll_multiplechoicequestion_options')

        # Deleting model 'SingleChoiceQuestion'
        db.delete_table('poll_singlechoicequestion')

        # Removing M2M table for field section on 'SingleChoiceQuestion'
        db.delete_table('poll_singlechoicequestion_section')

        # Removing M2M table for field options on 'SingleChoiceQuestion'
        db.delete_table('poll_singlechoicequestion_options')

        # Deleting model 'OpenQuestion'
        db.delete_table('poll_openquestion')

        # Removing M2M table for field section on 'OpenQuestion'
        db.delete_table('poll_openquestion_section')
    
    
    models = {
        'poll.multiplechoicequestion': {
            'Meta': {'object_name': 'MultipleChoiceQuestion'},
            'choice_limit': ('django.db.models.fields.IntegerField', [], {}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'has_other': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'section': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'symmetrical': 'False'})
        },
        'poll.openquestion': {
            'Meta': {'object_name': 'OpenQuestion'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'symmetrical': 'False'})
        },
        'poll.option': {
            'Meta': {'object_name': 'Option'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'poll.section': {
            'Meta': {'object_name': 'Section'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'poll.singlechoicequestion': {
            'Meta': {'object_name': 'SingleChoiceQuestion'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_scale': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'section': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'symmetrical': 'False'})
        }
    }
    
    complete_apps = ['poll']
