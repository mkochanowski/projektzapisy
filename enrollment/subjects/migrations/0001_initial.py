# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Subject'
        db.create_table('subjects_subject', (
            ('lectures', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exercises', self.gf('django.db.models.fields.IntegerField')()),
            ('laboratories', self.gf('django.db.models.fields.IntegerField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255, db_index=True)),
        ))
        db.send_create_signal('subjects', ['Subject'])

        # Adding model 'SubjectDescription'
        db.create_table('subjects_subjectdescription', (
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descriptions', to=orm['subjects.Subject'])),
        ))
        db.send_create_signal('subjects', ['SubjectDescription'])

        # Adding model 'Classroom'
        db.create_table('subjects_classroom', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal('subjects', ['Classroom'])

        # Adding model 'Term'
        db.create_table('subjects_term', (
            ('dayOfWeek', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hourFrom', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('hourTo', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('subjects', ['Term'])

        # Adding model 'Group'
        db.create_table('subjects_group', (
            ('limit', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Employee'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Subject'])),
        ))
        db.send_create_signal('subjects', ['Group'])

        # Adding M2M table for field classroom on 'Group'
        db.create_table('subjects_group_classroom', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['subjects.group'], null=False)),
            ('classroom', models.ForeignKey(orm['subjects.classroom'], null=False))
        ))
        db.create_unique('subjects_group_classroom', ['group_id', 'classroom_id'])

        # Adding M2M table for field term on 'Group'
        db.create_table('subjects_group_term', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['subjects.group'], null=False)),
            ('term', models.ForeignKey(orm['subjects.term'], null=False))
        ))
        db.create_unique('subjects_group_term', ['group_id', 'term_id'])

        # Adding model 'Books'
        db.create_table('subjects_books', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Subject'])),
        ))
        db.send_create_signal('subjects', ['Books'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Subject'
        db.delete_table('subjects_subject')

        # Deleting model 'SubjectDescription'
        db.delete_table('subjects_subjectdescription')

        # Deleting model 'Classroom'
        db.delete_table('subjects_classroom')

        # Deleting model 'Term'
        db.delete_table('subjects_term')

        # Deleting model 'Group'
        db.delete_table('subjects_group')

        # Removing M2M table for field classroom on 'Group'
        db.delete_table('subjects_group_classroom')

        # Removing M2M table for field term on 'Group'
        db.delete_table('subjects_group_term')

        # Deleting model 'Books'
        db.delete_table('subjects_books')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'subjects.books': {
            'Meta': {'object_name': 'Books'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Subject']"})
        },
        'subjects.classroom': {
            'Meta': {'object_name': 'Classroom'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        'subjects.group': {
            'Meta': {'object_name': 'Group'},
            'classroom': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'grupy'", 'to': "orm['subjects.Classroom']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Subject']"}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']"}),
            'term': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'grupy'", 'to': "orm['subjects.Term']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'subjects.subject': {
            'Meta': {'object_name': 'Subject'},
            'exercises': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {}),
            'lectures': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        'subjects.subjectdescription': {
            'Meta': {'object_name': 'SubjectDescription'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descriptions'", 'to': "orm['subjects.Subject']"})
        },
        'subjects.term': {
            'Meta': {'object_name': 'Term'},
            'dayOfWeek': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'hourFrom': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'hourTo': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'users.employee': {
            'Meta': {'object_name': 'Employee'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }
    
    complete_apps = ['subjects']
