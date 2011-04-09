# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Type'
        db.create_table('subjects_type', (
            ('meta_type', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Type'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
        ))
        db.send_create_signal('subjects', ['Type'])

        # Adding model 'StudentOptions'
        db.create_table('subjects_studentoptions', (
            ('records_opening_delay_minutes', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Student'])),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Subject'])),
        ))
        db.send_create_signal('subjects', ['StudentOptions'])

        # Adding unique constraint on 'StudentOptions', fields ['subject', 'student']
        db.create_unique('subjects_studentoptions', ['subject_id', 'student_id'])

        # Adding model 'SubjectEntity'
        db.create_table('subjects_subjectentity', (
            ('shortName', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('subjects', ['SubjectEntity'])

        # Adding model 'Subject'
        db.create_table('subjects_subject', (
            ('lectures', self.gf('django.db.models.fields.IntegerField')()),
            ('laboratories', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('repetitions', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('semester', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Semester'], null=True)),
            ('exercises', self.gf('django.db.models.fields.IntegerField')()),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.SubjectEntity'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Type'], null=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('subjects', ['Subject'])

        # Adding unique constraint on 'Subject', fields ['name', 'semester']
        db.create_unique('subjects_subject', ['name', 'semester_id'])

        # Adding M2M table for field teachers on 'Subject'
        db.create_table('subjects_subject_teachers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subject', models.ForeignKey(orm['subjects.subject'], null=False)),
            ('employee', models.ForeignKey(orm['users.employee'], null=False))
        ))
        db.create_unique('subjects_subject_teachers', ['subject_id', 'employee_id'])

        # Adding model 'Group'
        db.create_table('subjects_group', (
            ('limit', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Employee'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='groups', to=orm['subjects.Subject'])),
        ))
        db.send_create_signal('subjects', ['Group'])

        # Adding model 'Classroom'
        db.create_table('subjects_classroom', (
            ('building', self.gf('django.db.models.fields.CharField')(default='', max_length=75, blank=True)),
            ('capacity', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal('subjects', ['Classroom'])

        # Adding model 'Term'
        db.create_table('subjects_term', (
            ('dayOfWeek', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('classroom', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Classroom'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='term', to=orm['subjects.Group'])),
            ('start_time', self.gf('django.db.models.fields.TimeField')()),
            ('end_time', self.gf('django.db.models.fields.TimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('subjects', ['Term'])

        # Adding model 'Book'
        db.create_table('subjects_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(related_name='books', to=orm['subjects.Subject'])),
        ))
        db.send_create_signal('subjects', ['Book'])

        # Adding model 'Semester'
        db.create_table('subjects_semester', (
            ('records_opening', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('semester_beginning', self.gf('django.db.models.fields.DateField')()),
            ('semester_ending', self.gf('django.db.models.fields.DateField')()),
            ('records_closing', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('year', self.gf('django.db.models.fields.CharField')(default='0', max_length=7)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_grade_active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('subjects', ['Semester'])

        # Adding unique constraint on 'Semester', fields ['type', 'year']
        db.create_unique('subjects_semester', ['type', 'year'])

        # Adding model 'PointTypes'
        db.create_table('subjects_pointtypes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=30)),
        ))
        db.send_create_signal('subjects', ['PointTypes'])

        # Adding model 'PointsOfSubjectEntities'
        db.create_table('subjects_pointsofsubjectentities', (
            ('value', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type_of_point', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.PointTypes'])),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.SubjectEntity'])),
        ))
        db.send_create_signal('subjects', ['PointsOfSubjectEntities'])

        # Adding model 'PointsOfSubjects'
        db.create_table('subjects_pointsofsubjects', (
            ('value', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('program', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['users.Program'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type_of_point', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.PointTypes'])),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subjects.Subject'])),
        ))
        db.send_create_signal('subjects', ['PointsOfSubjects'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Type'
        db.delete_table('subjects_type')

        # Deleting model 'StudentOptions'
        db.delete_table('subjects_studentoptions')

        # Removing unique constraint on 'StudentOptions', fields ['subject', 'student']
        db.delete_unique('subjects_studentoptions', ['subject_id', 'student_id'])

        # Deleting model 'SubjectEntity'
        db.delete_table('subjects_subjectentity')

        # Deleting model 'Subject'
        db.delete_table('subjects_subject')

        # Removing unique constraint on 'Subject', fields ['name', 'semester']
        db.delete_unique('subjects_subject', ['name', 'semester_id'])

        # Removing M2M table for field teachers on 'Subject'
        db.delete_table('subjects_subject_teachers')

        # Deleting model 'Group'
        db.delete_table('subjects_group')

        # Deleting model 'Classroom'
        db.delete_table('subjects_classroom')

        # Deleting model 'Term'
        db.delete_table('subjects_term')

        # Deleting model 'Book'
        db.delete_table('subjects_book')

        # Deleting model 'Semester'
        db.delete_table('subjects_semester')

        # Removing unique constraint on 'Semester', fields ['type', 'year']
        db.delete_unique('subjects_semester', ['type', 'year'])

        # Deleting model 'PointTypes'
        db.delete_table('subjects_pointtypes')

        # Deleting model 'PointsOfSubjectEntities'
        db.delete_table('subjects_pointsofsubjectentities')

        # Deleting model 'PointsOfSubjects'
        db.delete_table('subjects_pointsofsubjects')
    
    
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
        'subjects.book': {
            'Meta': {'object_name': 'Book'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'books'", 'to': "orm['subjects.Subject']"})
        },
        'subjects.classroom': {
            'Meta': {'object_name': 'Classroom'},
            'building': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'capacity': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        'subjects.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['subjects.Subject']"}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'subjects.pointsofsubjectentities': {
            'Meta': {'object_name': 'PointsOfSubjectEntities'},
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.SubjectEntity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type_of_point': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.PointTypes']"}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'subjects.pointsofsubjects': {
            'Meta': {'object_name': 'PointsOfSubjects'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['users.Program']", 'null': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Subject']"}),
            'type_of_point': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.PointTypes']"}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'subjects.pointtypes': {
            'Meta': {'object_name': 'PointTypes'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'shortName': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'})
        },
        'subjects.term': {
            'Meta': {'object_name': 'Term'},
            'classroom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subjects.Classroom']"}),
            'dayOfWeek': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'term'", 'to': "orm['subjects.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
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
    
    complete_apps = ['subjects']
