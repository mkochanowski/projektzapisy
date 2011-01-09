# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'OpenQuestionOrdering.section'
        db.delete_column('poll_openquestionordering', 'section_id')

        # Adding field 'OpenQuestionOrdering.sections'
        db.add_column('poll_openquestionordering', 'sections', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['poll.Section']), keep_default=False)

        # Removing unique constraint on 'OpenQuestionOrdering', fields ['position', 'section']
        db.delete_unique('poll_openquestionordering', ['position', 'section_id'])

        # Adding unique constraint on 'OpenQuestionOrdering', fields ['position', 'sections']
        db.create_unique('poll_openquestionordering', ['position', 'sections_id'])

        # Deleting field 'MultipleChoiceQuestionOrdering.section'
        db.delete_column('poll_multiplechoicequestionordering', 'section_id')

        # Adding field 'MultipleChoiceQuestionOrdering.sections'
        db.add_column('poll_multiplechoicequestionordering', 'sections', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['poll.Section']), keep_default=False)

        # Removing unique constraint on 'MultipleChoiceQuestionOrdering', fields ['position', 'section']
        db.delete_unique('poll_multiplechoicequestionordering', ['position', 'section_id'])

        # Adding unique constraint on 'MultipleChoiceQuestionOrdering', fields ['position', 'sections']
        db.create_unique('poll_multiplechoicequestionordering', ['position', 'sections_id'])

        # Deleting field 'SingleChoiceQuestionOrdering.section'
        db.delete_column('poll_singlechoicequestionordering', 'section_id')

        # Adding field 'SingleChoiceQuestionOrdering.sections'
        db.add_column('poll_singlechoicequestionordering', 'sections', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['poll.Section']), keep_default=False)

        # Removing unique constraint on 'SingleChoiceQuestionOrdering', fields ['is_leading', 'section', 'position']
        db.delete_unique('poll_singlechoicequestionordering', ['is_leading', 'section_id', 'position'])

        # Adding unique constraint on 'SingleChoiceQuestionOrdering', fields ['is_leading', 'sections', 'position']
        db.create_unique('poll_singlechoicequestionordering', ['is_leading', 'sections_id', 'position'])
    
    
    def backwards(self, orm):
        
        # Adding field 'OpenQuestionOrdering.section'
        db.add_column('poll_openquestionordering', 'section', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['poll.Section']), keep_default=False)

        # Deleting field 'OpenQuestionOrdering.sections'
        db.delete_column('poll_openquestionordering', 'sections_id')

        # Adding unique constraint on 'OpenQuestionOrdering', fields ['position', 'section']
        db.create_unique('poll_openquestionordering', ['position', 'section_id'])

        # Removing unique constraint on 'OpenQuestionOrdering', fields ['position', 'sections']
        db.delete_unique('poll_openquestionordering', ['position', 'sections_id'])

        # Adding field 'MultipleChoiceQuestionOrdering.section'
        db.add_column('poll_multiplechoicequestionordering', 'section', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['poll.Section']), keep_default=False)

        # Deleting field 'MultipleChoiceQuestionOrdering.sections'
        db.delete_column('poll_multiplechoicequestionordering', 'sections_id')

        # Adding unique constraint on 'MultipleChoiceQuestionOrdering', fields ['position', 'section']
        db.create_unique('poll_multiplechoicequestionordering', ['position', 'section_id'])

        # Removing unique constraint on 'MultipleChoiceQuestionOrdering', fields ['position', 'sections']
        db.delete_unique('poll_multiplechoicequestionordering', ['position', 'sections_id'])

        # Adding field 'SingleChoiceQuestionOrdering.section'
        db.add_column('poll_singlechoicequestionordering', 'section', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['poll.Section']), keep_default=False)

        # Deleting field 'SingleChoiceQuestionOrdering.sections'
        db.delete_column('poll_singlechoicequestionordering', 'sections_id')

        # Adding unique constraint on 'SingleChoiceQuestionOrdering', fields ['is_leading', 'section', 'position']
        db.create_unique('poll_singlechoicequestionordering', ['is_leading', 'section_id', 'position'])

        # Removing unique constraint on 'SingleChoiceQuestionOrdering', fields ['is_leading', 'sections', 'position']
        db.delete_unique('poll_singlechoicequestionordering', ['is_leading', 'sections_id', 'position'])
    
    
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
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.MultipleChoiceQuestionOrdering']", 'symmetrical': 'False'})
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
            'Meta': {'unique_together': "(['sections', 'position'],)", 'object_name': 'MultipleChoiceQuestionOrdering'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.MultipleChoiceQuestion']"}),
            'sections': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"})
        },
        'poll.openquestion': {
            'Meta': {'object_name': 'OpenQuestion'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.OpenQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.openquestionanswer': {
            'Meta': {'object_name': 'OpenQuestionAnswer'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.OpenQuestion']"}),
            'saved_ticket': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.SavedTicket']", 'symmetrical': 'False'})
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
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Semester']"}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_scale': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Option']", 'symmetrical': 'False'}),
            'sections': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.Section']", 'through': "orm['poll.SingleChoiceQuestionOrdering']", 'symmetrical': 'False'})
        },
        'poll.singlechoicequestionanswer': {
            'Meta': {'object_name': 'SingleChoiceQuestionAnswer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Option']"}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.SingleChoiceQuestion']"}),
            'saved_ticket': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['poll.SavedTicket']", 'symmetrical': 'False'})
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
            'records_closing': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'records_opening': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'semester_begining': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'semester_ending': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2011'})
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
