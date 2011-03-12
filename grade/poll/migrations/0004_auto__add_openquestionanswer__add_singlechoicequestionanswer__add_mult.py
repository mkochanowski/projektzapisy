# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'OpenQuestionAnswer'
        db.create_table('poll_openquestionanswer', (
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.OpenQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['OpenQuestionAnswer'])

        # Adding M2M table for field saved_ticket on 'OpenQuestionAnswer'
        db.create_table('poll_openquestionanswer_saved_ticket', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('openquestionanswer', models.ForeignKey(orm['poll.openquestionanswer'], null=False)),
            ('savedticket', models.ForeignKey(orm['poll.savedticket'], null=False))
        ))
        db.create_unique('poll_openquestionanswer_saved_ticket', ['openquestionanswer_id', 'savedticket_id'])

        # Adding model 'SingleChoiceQuestionAnswer'
        db.create_table('poll_singlechoicequestionanswer', (
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.SingleChoiceQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('option', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Option'])),
        ))
        db.send_create_signal('poll', ['SingleChoiceQuestionAnswer'])

        # Adding M2M table for field saved_ticket on 'SingleChoiceQuestionAnswer'
        db.create_table('poll_singlechoicequestionanswer_saved_ticket', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('singlechoicequestionanswer', models.ForeignKey(orm['poll.singlechoicequestionanswer'], null=False)),
            ('savedticket', models.ForeignKey(orm['poll.savedticket'], null=False))
        ))
        db.create_unique('poll_singlechoicequestionanswer_saved_ticket', ['singlechoicequestionanswer_id', 'savedticket_id'])

        # Adding model 'MultipleChoiceQuestionAnswer'
        db.create_table('poll_multiplechoicequestionanswer', (
            ('other', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.MultipleChoiceQuestion'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['MultipleChoiceQuestionAnswer'])

        # Adding M2M table for field saved_ticket on 'MultipleChoiceQuestionAnswer'
        db.create_table('poll_multiplechoicequestionanswer_saved_ticket', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multiplechoicequestionanswer', models.ForeignKey(orm['poll.multiplechoicequestionanswer'], null=False)),
            ('savedticket', models.ForeignKey(orm['poll.savedticket'], null=False))
        ))
        db.create_unique('poll_multiplechoicequestionanswer_saved_ticket', ['multiplechoicequestionanswer_id', 'savedticket_id'])

        # Adding M2M table for field options on 'MultipleChoiceQuestionAnswer'
        db.create_table('poll_multiplechoicequestionanswer_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multiplechoicequestionanswer', models.ForeignKey(orm['poll.multiplechoicequestionanswer'], null=False)),
            ('option', models.ForeignKey(orm['poll.option'], null=False))
        ))
        db.create_unique('poll_multiplechoicequestionanswer_options', ['multiplechoicequestionanswer_id', 'option_id'])

        # Adding model 'SavedTicket'
        db.create_table('poll_savedticket', (
            ('ticket', self.gf('django.db.models.fields.TextField')()),
            ('poll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Poll'])),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['SavedTicket'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'OpenQuestionAnswer'
        db.delete_table('poll_openquestionanswer')

        # Removing M2M table for field saved_ticket on 'OpenQuestionAnswer'
        db.delete_table('poll_openquestionanswer_saved_ticket')

        # Deleting model 'SingleChoiceQuestionAnswer'
        db.delete_table('poll_singlechoicequestionanswer')

        # Removing M2M table for field saved_ticket on 'SingleChoiceQuestionAnswer'
        db.delete_table('poll_singlechoicequestionanswer_saved_ticket')

        # Deleting model 'MultipleChoiceQuestionAnswer'
        db.delete_table('poll_multiplechoicequestionanswer')

        # Removing M2M table for field saved_ticket on 'MultipleChoiceQuestionAnswer'
        db.delete_table('poll_multiplechoicequestionanswer_saved_ticket')

        # Removing M2M table for field options on 'MultipleChoiceQuestionAnswer'
        db.delete_table('poll_multiplechoicequestionanswer_options')

        # Deleting model 'SavedTicket'
        db.delete_table('poll_savedticket')
    
    
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
            'has_other': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'section': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.MultipleChoiceQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.multiplechoicequestionanswer': {
            'Meta': {'object_name': 'MultipleChoiceQuestionAnswer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.MultipleChoiceQuestion']"}),
            'saved_ticket': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.SavedTicket']", 'symmetrical': 'False'})
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
        'poll.openquestionanswer': {
            'Meta': {'object_name': 'OpenQuestionAnswer'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.OpenQuestion']"}),
            'saved_ticket': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.SavedTicket']", 'symmetrical': 'False'})
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
        'poll.poll': {
            'Meta': {'object_name': 'Poll'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'studies_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Type']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'poll.savedticket': {
            'Meta': {'object_name': 'SavedTicket'},
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Poll']"}),
            'ticket': ('django.db.models.fields.TextField', [], {})
        },
        'poll.section': {
            'Meta': {'object_name': 'Section'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_scale': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'section': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.SingleChoiceQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.singlechoicequestionanswer': {
            'Meta': {'object_name': 'SingleChoiceQuestionAnswer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Option']"}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.SingleChoiceQuestion']"}),
            'saved_ticket': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.SavedTicket']", 'symmetrical': 'False'})
        },
        'poll.singlechoicequestionordering': {
            'Meta': {'unique_together': "(['section', 'is_leading', 'position'],)", 'object_name': 'SingleChoiceQuestionOrdering'},
            'hide_on': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_leading': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.SingleChoiceQuestion']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
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
            'records_closing': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'records_opening': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2010'})
        },
        'subjects.studentoptions': {
            'Meta': {'unique_together': "(('subject', 'student'),)", 'object_name': 'StudentOptions'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'records_opening_delay_hours': ('django.db.models.fields.IntegerField', [], {}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Student']"}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Subject']"})
        },
        'subjects.subject': {
            'Meta': {'object_name': 'Subject'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'ects': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.SubjectEntity']"}),
            'exercises': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {}),
            'lectures': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Semester']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'students_options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Student']", 'through': "orm['subjects.StudentOptions']", 'symmetrical': 'False'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Employee']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Type']", 'null': 'True'})
        },
        'subjects.subjectentity': {
            'Meta': {'object_name': 'SubjectEntity'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'subjects.type': {
            'Meta': {'object_name': 'Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '30'})
        },
        'users.employee': {
            'Meta': {'object_name': 'Employee'},
            'consultations': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'users.student': {
            'Meta': {'object_name': 'Student'},
            'ects': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matricula': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '20'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'records_opening_delay_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Type']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'users.type': {
            'Meta': {'object_name': 'Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }
    
    complete_apps = ['poll']
