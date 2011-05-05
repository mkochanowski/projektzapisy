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

        # Adding model 'SavedTicket'
        db.create_table('poll_savedticket', (
            ('ticket', self.gf('django.db.models.fields.TextField')()),
            ('poll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Poll'])),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['SavedTicket'])

        # Adding unique constraint on 'SavedTicket', fields ['ticket', 'poll']
        db.create_unique('poll_savedticket', ['ticket', 'poll_id'])

        # Adding model 'MultipleChoiceQuestion'
        db.create_table('poll_multiplechoicequestion', (
            ('content', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('choice_limit', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('has_other', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('poll', ['MultipleChoiceQuestion'])

        # Adding M2M table for field options on 'MultipleChoiceQuestion'
        db.create_table('poll_multiplechoicequestion_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multiplechoicequestion', models.ForeignKey(orm['poll.multiplechoicequestion'], null=False)),
            ('option', models.ForeignKey(orm['poll.option'], null=False))
        ))
        db.create_unique('poll_multiplechoicequestion_options', ['multiplechoicequestion_id', 'option_id'])

        # Adding model 'MultipleChoiceQuestionOrdering'
        db.create_table('poll_multiplechoicequestionordering', (
            ('sections', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.MultipleChoiceQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('poll', ['MultipleChoiceQuestionOrdering'])

        # Adding unique constraint on 'MultipleChoiceQuestionOrdering', fields ['sections', 'position']
        db.create_unique('poll_multiplechoicequestionordering', ['sections_id', 'position'])

        # Adding model 'SingleChoiceQuestion'
        db.create_table('poll_singlechoicequestion', (
            ('content', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('is_scale', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('poll', ['SingleChoiceQuestion'])

        # Adding M2M table for field options on 'SingleChoiceQuestion'
        db.create_table('poll_singlechoicequestion_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('singlechoicequestion', models.ForeignKey(orm['poll.singlechoicequestion'], null=False)),
            ('option', models.ForeignKey(orm['poll.option'], null=False))
        ))
        db.create_unique('poll_singlechoicequestion_options', ['singlechoicequestion_id', 'option_id'])

        # Adding model 'SingleChoiceQuestionOrdering'
        db.create_table('poll_singlechoicequestionordering', (
            ('is_leading', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('sections', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.SingleChoiceQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('poll', ['SingleChoiceQuestionOrdering'])

        # Adding unique constraint on 'SingleChoiceQuestionOrdering', fields ['sections', 'is_leading', 'position']
        db.create_unique('poll_singlechoicequestionordering', ['sections_id', 'is_leading', 'position'])

        # Adding M2M table for field hide_on on 'SingleChoiceQuestionOrdering'
        db.create_table('poll_singlechoicequestionordering_hide_on', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('singlechoicequestionordering', models.ForeignKey(orm['poll.singlechoicequestionordering'], null=False)),
            ('option', models.ForeignKey(orm['poll.option'], null=False))
        ))
        db.create_unique('poll_singlechoicequestionordering_hide_on', ['singlechoicequestionordering_id', 'option_id'])

        # Adding model 'OpenQuestion'
        db.create_table('poll_openquestion', (
            ('content', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('poll', ['OpenQuestion'])

        # Adding model 'OpenQuestionOrdering'
        db.create_table('poll_openquestionordering', (
            ('sections', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.OpenQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('poll', ['OpenQuestionOrdering'])

        # Adding unique constraint on 'OpenQuestionOrdering', fields ['sections', 'position']
        db.create_unique('poll_openquestionordering', ['sections_id', 'position'])

        # Adding model 'Section'
        db.create_table('poll_section', (
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('poll', ['Section'])

        # Adding model 'SectionOrdering'
        db.create_table('poll_sectionordering', (
            ('position', self.gf('django.db.models.fields.IntegerField')()),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('poll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Poll'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['SectionOrdering'])

        # Adding unique constraint on 'SectionOrdering', fields ['poll', 'position']
        db.create_unique('poll_sectionordering', ['poll_id', 'position'])

        # Adding model 'Poll'
        db.create_table('poll_poll', (
            ('studies_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Program'], null=True, blank=True)),
            ('share_result', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Group'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='author', to=orm['users.Employee'])),
            ('semester', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Semester'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['Poll'])

        # Adding model 'OpenQuestionAnswer'
        db.create_table('poll_openquestionanswer', (
            ('content', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.OpenQuestion'])),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('saved_ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.SavedTicket'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['OpenQuestionAnswer'])

        # Adding model 'SingleChoiceQuestionAnswer'
        db.create_table('poll_singlechoicequestionanswer', (
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.SingleChoiceQuestion'])),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('saved_ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.SavedTicket'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Option'], null=True, blank=True)),
        ))
        db.send_create_signal('poll', ['SingleChoiceQuestionAnswer'])

        # Adding model 'MultipleChoiceQuestionAnswer'
        db.create_table('poll_multiplechoicequestionanswer', (
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.MultipleChoiceQuestion'])),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('other', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('saved_ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.SavedTicket'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['MultipleChoiceQuestionAnswer'])

        # Adding M2M table for field options on 'MultipleChoiceQuestionAnswer'
        db.create_table('poll_multiplechoicequestionanswer_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multiplechoicequestionanswer', models.ForeignKey(orm['poll.multiplechoicequestionanswer'], null=False)),
            ('option', models.ForeignKey(orm['poll.option'], null=False))
        ))
        db.create_unique('poll_multiplechoicequestionanswer_options', ['multiplechoicequestionanswer_id', 'option_id'])

        # Adding model 'Template'
        db.create_table('poll_template', (
            ('studies_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Program'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Employee'])),
            ('no_subject', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Subject'], null=True, blank=True)),
        ))
        db.send_create_signal('poll', ['Template'])

        # Adding model 'TemplateSections'
        db.create_table('poll_templatesections', (
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Template'])),
        ))
        db.send_create_signal('poll', ['TemplateSections'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Option'
        db.delete_table('poll_option')

        # Deleting model 'SavedTicket'
        db.delete_table('poll_savedticket')

        # Removing unique constraint on 'SavedTicket', fields ['ticket', 'poll']
        db.delete_unique('poll_savedticket', ['ticket', 'poll_id'])

        # Deleting model 'MultipleChoiceQuestion'
        db.delete_table('poll_multiplechoicequestion')

        # Removing M2M table for field options on 'MultipleChoiceQuestion'
        db.delete_table('poll_multiplechoicequestion_options')

        # Deleting model 'MultipleChoiceQuestionOrdering'
        db.delete_table('poll_multiplechoicequestionordering')

        # Removing unique constraint on 'MultipleChoiceQuestionOrdering', fields ['sections', 'position']
        db.delete_unique('poll_multiplechoicequestionordering', ['sections_id', 'position'])

        # Deleting model 'SingleChoiceQuestion'
        db.delete_table('poll_singlechoicequestion')

        # Removing M2M table for field options on 'SingleChoiceQuestion'
        db.delete_table('poll_singlechoicequestion_options')

        # Deleting model 'SingleChoiceQuestionOrdering'
        db.delete_table('poll_singlechoicequestionordering')

        # Removing unique constraint on 'SingleChoiceQuestionOrdering', fields ['sections', 'is_leading', 'position']
        db.delete_unique('poll_singlechoicequestionordering', ['sections_id', 'is_leading', 'position'])

        # Removing M2M table for field hide_on on 'SingleChoiceQuestionOrdering'
        db.delete_table('poll_singlechoicequestionordering_hide_on')

        # Deleting model 'OpenQuestion'
        db.delete_table('poll_openquestion')

        # Deleting model 'OpenQuestionOrdering'
        db.delete_table('poll_openquestionordering')

        # Removing unique constraint on 'OpenQuestionOrdering', fields ['sections', 'position']
        db.delete_unique('poll_openquestionordering', ['sections_id', 'position'])

        # Deleting model 'Section'
        db.delete_table('poll_section')

        # Deleting model 'SectionOrdering'
        db.delete_table('poll_sectionordering')

        # Removing unique constraint on 'SectionOrdering', fields ['poll', 'position']
        db.delete_unique('poll_sectionordering', ['poll_id', 'position'])

        # Deleting model 'Poll'
        db.delete_table('poll_poll')

        # Deleting model 'OpenQuestionAnswer'
        db.delete_table('poll_openquestionanswer')

        # Deleting model 'SingleChoiceQuestionAnswer'
        db.delete_table('poll_singlechoicequestionanswer')

        # Deleting model 'MultipleChoiceQuestionAnswer'
        db.delete_table('poll_multiplechoicequestionanswer')

        # Removing M2M table for field options on 'MultipleChoiceQuestionAnswer'
        db.delete_table('poll_multiplechoicequestionanswer_options')

        # Deleting model 'Template'
        db.delete_table('poll_template')

        # Deleting model 'TemplateSections'
        db.delete_table('poll_templatesections')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'poll.multiplechoicequestion': {
            'Meta': {'object_name': 'MultipleChoiceQuestion'},
            'choice_limit': ('django.db.models.fields.IntegerField', [], {}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'has_other': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.MultipleChoiceQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.multiplechoicequestionanswer': {
            'Meta': {'object_name': 'MultipleChoiceQuestionAnswer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['poll.Option']", 'null': 'True', 'blank': 'True'}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.MultipleChoiceQuestion']"}),
            'saved_ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.SavedTicket']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        },
        'poll.multiplechoicequestionordering': {
            'Meta': {'unique_together': "(['sections', 'position'],)", 'object_name': 'MultipleChoiceQuestionOrdering'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.MultipleChoiceQuestion']"}),
            'sections': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        },
        'poll.openquestion': {
            'Meta': {'object_name': 'OpenQuestion'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.OpenQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.openquestionanswer': {
            'Meta': {'object_name': 'OpenQuestionAnswer'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.OpenQuestion']"}),
            'saved_ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.SavedTicket']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        },
        'poll.openquestionordering': {
            'Meta': {'unique_together': "(['sections', 'position'],)", 'object_name': 'OpenQuestionOrdering'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.OpenQuestion']"}),
            'sections': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        },
        'poll.option': {
            'Meta': {'object_name': 'Option'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'poll.poll': {
            'Meta': {'object_name': 'Poll'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'author'", 'to': "orm['users.Employee']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Semester']"}),
            'share_result': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'studies_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Program']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'poll.savedticket': {
            'Meta': {'unique_together': "(['ticket', 'poll'],)", 'object_name': 'SavedTicket'},
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Poll']"}),
            'ticket': ('django.db.models.fields.TextField', [], {})
        },
        'poll.section': {
            'Meta': {'object_name': 'Section'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Poll']", 'through': "orm['poll.SectionOrdering']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'poll.sectionordering': {
            'Meta': {'unique_together': "(['poll', 'position'],)", 'object_name': 'SectionOrdering'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Poll']"}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        },
        'poll.singlechoicequestion': {
            'Meta': {'object_name': 'SingleChoiceQuestion'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_scale': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.SingleChoiceQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.singlechoicequestionanswer': {
            'Meta': {'object_name': 'SingleChoiceQuestionAnswer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Option']", 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.SingleChoiceQuestion']"}),
            'saved_ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.SavedTicket']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        },
        'poll.singlechoicequestionordering': {
            'Meta': {'unique_together': "(['sections', 'is_leading', 'position'],)", 'object_name': 'SingleChoiceQuestionOrdering'},
            'hide_on': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_leading': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.SingleChoiceQuestion']"}),
            'sections': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        },
        'poll.template': {
            'Meta': {'object_name': 'Template'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'no_subject': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.TemplateSections']", 'symmetrical': 'False'}),
            'studies_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Program']", 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Subject']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'poll.templatesections': {
            'Meta': {'object_name': 'TemplateSections'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Template']"})
        },
        'subjects.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['subjects.Subject']"}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'subjects.semester': {
            'Meta': {'unique_together': "(('type', 'year'),)", 'object_name': 'Semester'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_grade_active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'records_closing': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'records_opening': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'semester_beginning': ('django.db.models.fields.DateField', [], {}),
            'semester_ending': ('django.db.models.fields.DateField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '7'})
        },
        'subjects.studentoptions': {
            'Meta': {'unique_together': "(('subject', 'student'),)", 'object_name': 'StudentOptions'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'records_opening_delay_minutes': ('django.db.models.fields.IntegerField', [], {}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Student']"}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Subject']"})
        },
        'subjects.subject': {
            'Meta': {'unique_together': "(('name', 'semester'),)", 'object_name': 'Subject'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.SubjectEntity']"}),
            'exercises': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {}),
            'lectures': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repetitions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Semester']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'db_index': 'True'}),
            'students_options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Student']", 'through': "orm['subjects.StudentOptions']", 'symmetrical': 'False'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Employee']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Type']", 'null': 'True'})
        },
        'subjects.subjectentity': {
            'Meta': {'object_name': 'SubjectEntity'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'exercises': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'lectures': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'repetitions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'shortName': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Type']", 'null': 'True'})
        },
        'subjects.type': {
            'Meta': {'object_name': 'Type'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Type']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_type': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'})
        },
        'users.employee': {
            'Meta': {'object_name': 'Employee'},
            'consultations': ('django.db.models.fields.TextField', [], {}),
            'homepage': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'room': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'users.program': {
            'Meta': {'object_name': 'Program'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'users.student': {
            'Meta': {'object_name': 'Student'},
            'block': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'ects': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matricula': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '20'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['users.Program']", 'null': 'True'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'records_opening_delay_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'semestr': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }
    
    complete_apps = ['poll']
