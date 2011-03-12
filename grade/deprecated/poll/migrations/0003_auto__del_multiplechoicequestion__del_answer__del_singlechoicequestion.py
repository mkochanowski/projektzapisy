# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'MultipleChoiceQuestion'
        db.delete_table('poll_multiplechoicequestion')

        # Removing M2M table for field answers on 'MultipleChoiceQuestion'
        db.delete_table('poll_multiplechoicequestion_answers')

        # Deleting model 'Answer'
        db.delete_table('poll_answer')

        # Deleting model 'SingleChoiceQuestion'
        db.delete_table('poll_singlechoicequestion')

        # Removing M2M table for field answers on 'SingleChoiceQuestion'
        db.delete_table('poll_singlechoicequestion_answers')

        # Deleting model 'OpenQuestion'
        db.delete_table('poll_openquestion')

        # Adding model 'Option'
        db.create_table('poll_option', (
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Question'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('poll', ['Option'])

        # Adding model 'Section'
        db.create_table('poll_section', (
            ('poll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Poll'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('poll', ['Section'])

        # Adding model 'Question'
        db.create_table('poll_question', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Section'])),
            ('poll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poll.Poll'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['Question'])

        # Deleting field 'Poll.group'
        db.delete_column('poll_poll', 'group_id')

        # Deleting field 'Poll.subject'
        db.delete_column('poll_poll', 'subject_id')

        # Removing M2M table for field open_questions on 'Poll'
        db.delete_table('poll_poll_open_questions')

        # Removing M2M table for field multiple_choice_question on 'Poll'
        db.delete_table('poll_poll_multiple_choice_question')

        # Removing M2M table for field single_choice_questions on 'Poll'
        db.delete_table('poll_poll_single_choice_questions')
    
    
    def backwards(self, orm):
        
        # Adding model 'MultipleChoiceQuestion'
        db.create_table('poll_multiplechoicequestion', (
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('has_other', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('reason', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contents', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('poll', ['MultipleChoiceQuestion'])

        # Adding M2M table for field answers on 'MultipleChoiceQuestion'
        db.create_table('poll_multiplechoicequestion_answers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('multiplechoicequestion', models.ForeignKey(orm['poll.multiplechoicequestion'], null=False)),
            ('answer', models.ForeignKey(orm['poll.answer'], null=False))
        ))
        db.create_unique('poll_multiplechoicequestion_answers', ['multiplechoicequestion_id', 'answer_id'])

        # Adding model 'Answer'
        db.create_table('poll_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contents', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('poll', ['Answer'])

        # Adding model 'SingleChoiceQuestion'
        db.create_table('poll_singlechoicequestion', (
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('has_other', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('reason', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contents', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('poll', ['SingleChoiceQuestion'])

        # Adding M2M table for field answers on 'SingleChoiceQuestion'
        db.create_table('poll_singlechoicequestion_answers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('singlechoicequestion', models.ForeignKey(orm['poll.singlechoicequestion'], null=False)),
            ('answer', models.ForeignKey(orm['poll.answer'], null=False))
        ))
        db.create_unique('poll_singlechoicequestion_answers', ['singlechoicequestion_id', 'answer_id'])

        # Adding model 'OpenQuestion'
        db.create_table('poll_openquestion', (
            ('reason', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('contents', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('poll', ['OpenQuestion'])

        # Deleting model 'Option'
        db.delete_table('poll_option')

        # Deleting model 'Section'
        db.delete_table('poll_section')

        # Deleting model 'Question'
        db.delete_table('poll_question')

        # Adding field 'Poll.group'
        db.add_column('poll_poll', 'group', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['subjects.Group']), keep_default=False)

        # Adding field 'Poll.subject'
        db.add_column('poll_poll', 'subject', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['subjects.Subject']), keep_default=False)

        # Adding M2M table for field open_questions on 'Poll'
        db.create_table('poll_poll_open_questions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('poll', models.ForeignKey(orm['poll.poll'], null=False)),
            ('openquestion', models.ForeignKey(orm['poll.openquestion'], null=False))
        ))
        db.create_unique('poll_poll_open_questions', ['poll_id', 'openquestion_id'])

        # Adding M2M table for field multiple_choice_question on 'Poll'
        db.create_table('poll_poll_multiple_choice_question', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('poll', models.ForeignKey(orm['poll.poll'], null=False)),
            ('multiplechoicequestion', models.ForeignKey(orm['poll.multiplechoicequestion'], null=False))
        ))
        db.create_unique('poll_poll_multiple_choice_question', ['poll_id', 'multiplechoicequestion_id'])

        # Adding M2M table for field single_choice_questions on 'Poll'
        db.create_table('poll_poll_single_choice_questions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('poll', models.ForeignKey(orm['poll.poll'], null=False)),
            ('singlechoicequestion', models.ForeignKey(orm['poll.singlechoicequestion'], null=False))
        ))
        db.create_unique('poll_poll_single_choice_questions', ['poll_id', 'singlechoicequestion_id'])
    
    
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
        'poll.option': {
            'Meta': {'object_name': 'Option'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'poll.poll': {
            'Meta': {'object_name': 'Poll'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'poll.question': {
            'Meta': {'object_name': 'Question'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Poll']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Section']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'poll.section': {
            'Meta': {'object_name': 'Section'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poll.Poll']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'users.employee': {
            'Meta': {'object_name': 'Employee'},
            'consultations': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }
    
    complete_apps = ['poll']
