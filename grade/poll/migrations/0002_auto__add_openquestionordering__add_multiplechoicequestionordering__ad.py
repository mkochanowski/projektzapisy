# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'OpenQuestionOrdering'
        db.create_table('poll_openquestionordering', (
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.OpenQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['OpenQuestionOrdering'])

        # Adding model 'MultipleChoiceQuestionOrdering'
        db.create_table('poll_multiplechoicequestionordering', (
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.MultipleChoiceQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['MultipleChoiceQuestionOrdering'])

        # Adding model 'SingleChoiceQuestionOrdering'
        db.create_table('poll_singlechoicequestionordering', (
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.SingleChoiceQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_leading', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('poll', ['SingleChoiceQuestionOrdering'])

        # Adding M2M table for field hide_on on 'SingleChoiceQuestionOrdering'
        db.create_table('poll_singlechoicequestionordering_hide_on', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('singlechoicequestionordering', models.ForeignKey(orm['poll.singlechoicequestionordering'], null=False)),
            ('option', models.ForeignKey(orm['poll.option'], null=False))
        ))
        db.create_unique('poll_singlechoicequestionordering_hide_on', ['singlechoicequestionordering_id', 'option_id'])

        # Removing M2M table for field section on 'MultipleChoiceQuestion'
        db.delete_table('poll_multiplechoicequestion_section')

        # Removing M2M table for field section on 'OpenQuestion'
        db.delete_table('poll_openquestion_section')

        # Removing M2M table for field section on 'SingleChoiceQuestion'
        db.delete_table('poll_singlechoicequestion_section')
    
    
    def backwards(self, orm):
        
        # Deleting model 'OpenQuestionOrdering'
        db.delete_table('poll_openquestionordering')

        # Deleting model 'MultipleChoiceQuestionOrdering'
        db.delete_table('poll_multiplechoicequestionordering')

        # Deleting model 'SingleChoiceQuestionOrdering'
        db.delete_table('poll_singlechoicequestionordering')

        # Removing M2M table for field hide_on on 'SingleChoiceQuestionOrdering'
        db.delete_table('poll_singlechoicequestionordering_hide_on')

        # Adding M2M table for field section on 'MultipleChoiceQuestion'
        db.create_table('poll_multiplechoicequestion_section', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multiplechoicequestion', models.ForeignKey(orm['poll.multiplechoicequestion'], null=False)),
            ('section', models.ForeignKey(orm['poll.section'], null=False))
        ))
        db.create_unique('poll_multiplechoicequestion_section', ['multiplechoicequestion_id', 'section_id'])

        # Adding M2M table for field section on 'OpenQuestion'
        db.create_table('poll_openquestion_section', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('openquestion', models.ForeignKey(orm['poll.openquestion'], null=False)),
            ('section', models.ForeignKey(orm['poll.section'], null=False))
        ))
        db.create_unique('poll_openquestion_section', ['openquestion_id', 'section_id'])

        # Adding M2M table for field section on 'SingleChoiceQuestion'
        db.create_table('poll_singlechoicequestion_section', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('singlechoicequestion', models.ForeignKey(orm['poll.singlechoicequestion'], null=False)),
            ('section', models.ForeignKey(orm['poll.section'], null=False))
        ))
        db.create_unique('poll_singlechoicequestion_section', ['singlechoicequestion_id', 'section_id'])
    
    
    models = {
        'poll.multiplechoicequestion': {
            'Meta': {'object_name': 'MultipleChoiceQuestion'},
            'choice_limit': ('django.db.models.fields.IntegerField', [], {}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'has_other': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'section': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.MultipleChoiceQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.multiplechoicequestionordering': {
            'Meta': {'unique_together': "(['section', 'position'],)", 'object_name': 'MultipleChoiceQuestionOrdering'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.MultipleChoiceQuestion']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        },
        'poll.openquestion': {
            'Meta': {'object_name': 'OpenQuestion'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.OpenQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.openquestionordering': {
            'Meta': {'unique_together': "(['section', 'position'],)", 'object_name': 'OpenQuestionOrdering'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.OpenQuestion']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
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
            'section': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.SingleChoiceQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.singlechoicequestionordering': {
            'Meta': {'unique_together': "(['section', 'is_leading', 'position'],)", 'object_name': 'SingleChoiceQuestionOrdering'},
            'hide_on': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_leading': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.SingleChoiceQuestion']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        }
    }
    
    complete_apps = ['poll']
