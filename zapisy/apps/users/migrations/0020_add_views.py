# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        db.execute("""CREATE OR REPLACE view users_minutes_bonus_view as
        SELECT
           us.id as student_id,
           cs.id as semester_id,
           ((SELECT COUNT(*) FROM ticket_create_studentgraded WHERE semester_id IN ( cs.first_grade_semester_id,  cs.second_grade_semester_id) AND ticket_create_studentgraded.student_id = us.id ) * 1440
             + us.ects * 5 + (us.ects * 5 /720)::integer * 720 + us.records_opening_bonus_minutes + 120 )::integer as minutes

        FROM users_student us, courses_semester cs
        WHERE cs.records_closing > now();


        CREATE OR REPLACE view users_openingtimesview_unmaterialized as SELECT
           cc.id as course_id,
           users_student.id as student_id,
           cc.semester_id as semester_id,
           cs.records_opening - ((v.minutes + COALESCE( (SELECT DISTINCT sv.correction FROM vote_singlevote sv WHERE sv.entity_id = cc.entity_id AND sv.state_id IN
                  (SELECT id FROM vote_systemstate vs WHERE vs.semester_summer_id = cc.semester_id OR vs.semester_winter_id = cc.semester_id) LIMIT 1),
                  0
           )*1440)::TEXT || ' MINUTES')::INTERVAL as opening_time

        FROM courses_course cc, users_student, courses_semester cs
             LEFT JOIN users_minutes_bonus_view v ON(v.semester_id = cs.id )
         WHERE
         users_student.status = 0 AND
         v.student_id= users_student.id AND
         cs.records_opening IS NOT NULL AND cc.semester_id = cs.id
         AND cs.records_closing > now();

        CREATE TABLE users_openingtimesview
                (
                  course_id integer,
                  student_id integer,
                  semester_id integer,
                  opening_time timestamp with time zone
                );

                -- Index: entity

                -- DROP INDEX entity;

                CREATE INDEX users_openingtimesview_course_index
                  ON users_openingtimesview
                  USING btree
                  (course_id );

                -- Index: student

                -- DROP INDEX student;

                CREATE INDEX users_openingtimesview_student_index
                  ON users_openingtimesview
                  USING btree
                  (student_id );

                -- Index: student_and_entity

                -- DROP INDEX student_and_entity;

                CREATE INDEX users_openingtimesview_student_and_course_index
                  ON users_openingtimesview
                  USING btree
                  (student_id , course_id );


        INSERT INTO users_openingtimesview (SELECT * FROM users_openingtimesview_unmaterialized);



        create or replace function users_openingtimesview_refresh_for_student(
         id integer
        ) returns void
        security definer
        language 'plpgsql' as $$
        begin
           delete from users_openingtimesview csp where csp.student_id = id;
           insert into users_openingtimesview
           SELECT * FROM users_openingtimesview_unmaterialized scp
             WHERE scp.student_id = id;
        end
        $$;



        create or replace function users_openingtimesview_refresh_for_semester(
         id integer
        ) returns void
        security definer
        language 'plpgsql' as $$
        begin
           delete from users_openingtimesview csp where csp.semester_id = id;
           insert into users_openingtimesview
           SELECT * FROM users_openingtimesview_unmaterialized scp
             WHERE scp.semester_id = id;
        end
        $$;


        create or replace function change_student_update_user_opening_times_it() returns trigger
        security definer language 'plpgsql' as $$
        begin
          perform  users_openingtimesview_refresh_for_student(new.id);
          return null;
        end
        $$;


        create or replace function change_student_update_user_opening_times_dt() returns trigger
        security definer language 'plpgsql' as $$
        begin
          perform  users_openingtimesview_refresh_for_student(old.id);
          return null;
        end
        $$;

        create or replace function change_student_update_user_opening_times_ut() returns trigger
        security definer language 'plpgsql' as $$
        begin
          if old.ects = new.ects and old.records_opening_bonus_minutes = new.records_opening_bonus_minutes then
             return null;
          end if;
          if old.id = new.id then
             perform users_openingtimesview_refresh_for_student(old.id);
             perform users_openingtimesview_refresh_for_student(new.id);
          else
             perform users_openingtimesview_refresh_for_student(new.id);
          end if;
          return null;
        end
        $$;


        create trigger change_student_update_points_insert after insert on users_student
          for each row execute procedure change_student_update_user_opening_times_it();

        create trigger change_student_update_points_delete after delete on users_student
          for each row execute procedure change_student_update_user_opening_times_dt();

        create trigger change_student_update_points_update after update on users_student
          for each row execute procedure change_student_update_user_opening_times_ut();



        create or replace function change_semester_update_user_opening_times_it() returns trigger
        security definer language 'plpgsql' as $$
        begin
          perform  users_openingtimesview_refresh_for_semester(new.id);
          return null;
        end
        $$;


        create or replace function change_semester_update_user_opening_times_dt() returns trigger
        security definer language 'plpgsql' as $$
        begin
          perform  users_openingtimesview_refresh_for_semester(old.id);
          return null;
        end
        $$;

        create or replace function change_semester_update_user_opening_times_ut() returns trigger
        security definer language 'plpgsql' as $$
        begin
          if old.records_opening = new.records_opening and old.first_grade_semester_id = new.first_grade_semester_id and old.second_grade_semester_id = new.second_grade_semester_id then
             return null;
          end if;

          if old.id = new.id then
             perform users_openingtimesview_refresh_for_semester(old.id);
             perform users_openingtimesview_refresh_for_semester(new.id);
          else
             perform users_openingtimesview_refresh_for_semester(new.id);
          end if;
          return null;
        end
        $$;



        create trigger change_semester_update_points_insert after insert on courses_semester
          for each row execute procedure change_semester_update_user_opening_times_it();

        create trigger change_semester_update_points_delete after delete on courses_semester
          for each row execute procedure change_semester_update_user_opening_times_dt();

        create trigger change_semester_update_points_update after update on courses_semester
          for each row execute procedure change_semester_update_user_opening_times_ut();

""")

    def backwards(self, orm):
        pass

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
        'courses.course': {
            'Meta': {'ordering': "['entity__name']", 'object_name': 'Course'},
            'english': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseDescription']", 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'records_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'records_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Semester']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'students_options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Student']", 'through': "orm['courses.StudentOptions']", 'symmetrical': 'False'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Employee']", 'symmetrical': 'False', 'blank': 'True'}),
            'web_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'courses.coursedescription': {
            'Meta': {'object_name': 'CourseDescription'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseEntity']"}),
            'exam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exercises': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'exercises_laboratories': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'lectures': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'repetitions': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'requirements': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': "orm['courses.CourseEntity']"}),
            'seminars': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'courses.courseentity': {
            'Meta': {'ordering': "['name']", 'object_name': 'CourseEntity'},
            'algorytmy_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dyskretna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'english': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exam': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'exercises': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exercises_laboratiories': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_prefs': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'information': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.CourseDescription']", 'null': 'True', 'blank': 'True'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'lectures': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeryczna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Employee']", 'null': 'True', 'blank': 'True'}),
            'programowanie_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repetitions': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'semester': ('django.db.models.fields.CharField', [], {'default': "'u'", 'max_length': '1'}),
            'seminars': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'shortName': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'suggested_for_first_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Type']", 'null': 'True'}),
            'ue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'usos_kod': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'web_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
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
            'first_grade_semester': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fgrade'", 'null': 'True', 'to': "orm['courses.Semester']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_grade_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lectures_beginning': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'lectures_ending': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'records_closing': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'records_ects_limit_abolition': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'records_opening': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'second_grade_semester': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sgrade'", 'null': 'True', 'to': "orm['courses.Semester']"}),
            'semester_beginning': ('django.db.models.fields.DateField', [], {}),
            'semester_ending': ('django.db.models.fields.DateField', [], {}),
            't0_are_ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'last_news_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 4, 0, 0)'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'employee'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'users.extendeduser': {
            'Meta': {'object_name': 'ExtendedUser', '_ormbases': ['auth.User']},
            'is_employee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_student': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_zamawiany': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'users.openingtimesview': {
            'Meta': {'object_name': 'OpeningTimesView'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'opening_time': ('django.db.models.fields.DateTimeField', [], {}),
            'semester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Semester']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'opening_times'", 'primary_key': 'True', 'to': "orm['users.Student']"})
        },
        'users.program': {
            'Meta': {'object_name': 'Program'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'type_of_points': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.PointTypes']"})
        },
        'users.student': {
            'Meta': {'ordering': "['user__last_name', 'user__first_name']", 'object_name': 'Student'},
            'algorytmy_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'block': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dyskretna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ects': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ects_in_semester': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_news_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 4, 0, 0)'}),
            'matricula': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '20'}),
            'numeryczna_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['users.Program']", 'null': 'True'}),
            'programowanie_l': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'records_opening_bonus_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'semestr': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            't0': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'student'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'users.studiazamawiane': {
            'Meta': {'object_name': 'StudiaZamawiane'},
            'bank_account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'zamawiane'", 'unique': 'True', 'to': "orm['users.Student']"})
        },
        'users.studiazamawiane2012': {
            'Meta': {'object_name': 'StudiaZamawiane2012'},
            'bank_account': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'zamawiane2012'", 'unique': 'True', 'to': "orm['users.Student']"})
        },
        'users.studiazamawianemaileopiekunow': {
            'Meta': {'object_name': 'StudiaZamawianeMaileOpiekunow'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'users.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_employee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_student': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_zamawiany': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'_profile_cache'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['users']
    symmetrical = True
