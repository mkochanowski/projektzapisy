# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CourseDescription.lectures'
        db.add_column('courses_coursedescription', 'lectures',
                      self.gf('timedelta.fields.TimedeltaField')(default=datetime.timedelta(0), null=True),
                      keep_default=False)

        # Adding field 'CourseDescription.repetitions'
        db.add_column('courses_coursedescription', 'repetitions',
                      self.gf('timedelta.fields.TimedeltaField')(default=datetime.timedelta(0), null=True),
                      keep_default=False)

        # Adding field 'CourseDescription.exercises'
        db.add_column('courses_coursedescription', 'exercises',
                      self.gf('timedelta.fields.TimedeltaField')(default=datetime.timedelta(0), null=True),
                      keep_default=False)

        # Adding field 'CourseDescription.laboratories'
        db.add_column('courses_coursedescription', 'laboratories',
                      self.gf('timedelta.fields.TimedeltaField')(default=datetime.timedelta(0), null=True),
                      keep_default=False)

        # Adding field 'CourseDescription.exercises_laboratories'
        db.add_column('courses_coursedescription', 'exercises_laboratories',
                      self.gf('timedelta.fields.TimedeltaField')(default=datetime.timedelta(0), null=True),
                      keep_default=False)

        # Adding field 'CourseDescription.seminars'
        db.add_column('courses_coursedescription', 'seminars',
                      self.gf('timedelta.fields.TimedeltaField')(default=datetime.timedelta(0), null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CourseDescription.lectures'
        db.delete_column('courses_coursedescription', 'lectures')

        # Deleting field 'CourseDescription.repetitions'
        db.delete_column('courses_coursedescription', 'repetitions')

        # Deleting field 'CourseDescription.exercises'
        db.delete_column('courses_coursedescription', 'exercises')

        # Deleting field 'CourseDescription.laboratories'
        db.delete_column('courses_coursedescription', 'laboratories')

        # Deleting field 'CourseDescription.exercises_laboratories'
        db.delete_column('courses_coursedescription', 'exercises_laboratories')

        # Deleting field 'CourseDescription.seminars'
        db.delete_column('courses_coursedescription', 'seminars')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'courses.book': {
            'Meta': {'object_name': 'Book'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'books'", 'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'courses.classroom': {
            'Meta': {'object_name': 'Classroom'},
            'building': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'capacity': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'courses.course': {
            'Meta': {'ordering': "['entity__name']", 'object_name': 'Course'},
            'dyskretna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'english': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'exam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseDescription']", 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'numeryczna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'records_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'records_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Semester']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'students_options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Student']", 'through': "orm['courses.StudentOptions']", 'symmetrical': 'False'}),
            'suggested_for_first_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Employee']", 'symmetrical': 'False', 'blank': 'True'}),
            'web_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'courses.coursedescription': {
            'Meta': {'object_name': 'CourseDescription'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'exam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exercises': ('timedelta.fields.TimedeltaField', [], {'default': 'datetime.timedelta(0)', 'null': 'True'}),
            'exercises_laboratories': ('timedelta.fields.TimedeltaField', [], {'default': 'datetime.timedelta(0)', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'laboratories': ('timedelta.fields.TimedeltaField', [], {'default': 'datetime.timedelta(0)', 'null': 'True'}),
            'lectures': ('timedelta.fields.TimedeltaField', [], {'default': 'datetime.timedelta(0)', 'null': 'True'}),
            'repetitions': ('timedelta.fields.TimedeltaField', [], {'default': 'datetime.timedelta(0)', 'null': 'True'}),
            'requirements': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': "orm['courses.CourseEntity']"}),
            'seminars': ('timedelta.fields.TimedeltaField', [], {'default': 'datetime.timedelta(0)', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Type']"})
        },
        'courses.courseentity': {
            'Meta': {'ordering': "['name']", 'object_name': 'CourseEntity'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'english': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exam': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'exercises': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exercises_laboratiories': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'have_lab': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'have_lecture': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'have_project': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'have_review_lecture': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'have_seminar': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'have_tutorial': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'have_tutorial_lab': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_prefs': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lectures': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']", 'null': 'True', 'blank': 'True'}),
            'repetitions': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'requirements': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['courses.CourseEntity']", 'null': 'True', 'blank': 'True'}),
            'semester': ('django.db.models.fields.CharField', [], {'default': "'u'", 'max_length': '1'}),
            'seminars': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shortName': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Type']", 'null': 'True'}),
            'usos_kod': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'web_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'courses.group': {
            'Meta': {'object_name': 'Group'},
            'cache_enrolled': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_enrolled_zam': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cache_queued': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['courses.Course']"}),
            'enrolled': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'enrolled_zam': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'enrolled_zam2012': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'export_usos': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'extra': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'limit_zamawiane': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'limit_zamawiane2012': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'queued': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'usos_nr': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'courses.pointsofcourseentities': {
            'Meta': {'unique_together': "(('entity', 'type_of_point', 'program'),)", 'object_name': 'PointsOfCourseEntities'},
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['users.Program']", 'null': 'True', 'blank': 'True'}),
            'type_of_point': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.PointTypes']"}),
            'value': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '6'})
        },
        'courses.pointtypes': {
            'Meta': {'object_name': 'PointTypes'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'})
        },
        'courses.semester': {
            'Meta': {'ordering': "['-year', 'type']", 'unique_together': "(('type', 'year'),)", 'object_name': 'Semester'},
            'desiderata_closing': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'desiderata_opening': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_grade_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'records_closing': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'records_ects_limit_abolition': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'records_opening': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'semester_beginning': ('django.db.models.fields.DateField', [], {}),
            'semester_ending': ('django.db.models.fields.DateField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'year': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '7'})
        },
        'courses.studentoptions': {
            'Meta': {'unique_together': "(('course', 'student'),)", 'object_name': 'StudentOptions'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'records_opening_bonus_minutes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Student']"})
        },
        'courses.term': {
            'Meta': {'ordering': "['dayOfWeek']", 'object_name': 'Term'},
            'classroom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Classroom']", 'null': 'True', 'blank': 'True'}),
            'classrooms': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'new_classrooms'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['courses.Classroom']"}),
            'dayOfWeek': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'term'", 'to': "orm['courses.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        'courses.type': {
            'Meta': {'object_name': 'Type'},
            'free_in_vote': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Type']", 'null': 'True', 'blank': 'True'}),
            'have_lab': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_lecture': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_project': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_review_lecture': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_seminar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_tutorial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'have_tutorial_lab': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'short_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5'})
        },
        'users.employee': {
            'Meta': {'ordering': "['user__last_name', 'user__first_name']", 'object_name': 'Employee'},
            'consultations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_news_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 30, 0, 0)'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'employee'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'users.program': {
            'Meta': {'object_name': 'Program'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'type_of_points': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.PointTypes']"})
        },
        'users.student': {
            'Meta': {'ordering': "['user__last_name', 'user__first_name']", 'object_name': 'Student'},
            'block': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dyskretna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ects': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ects_in_semester': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_news_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 30, 0, 0)'}),
            'matricula': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '20'}),
            'numeryczna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['users.Program']", 'null': 'True'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'records_opening_bonus_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'semestr': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            't0': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'student'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['courses']