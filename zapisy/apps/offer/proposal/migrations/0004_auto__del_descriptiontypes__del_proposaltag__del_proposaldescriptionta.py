# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'DescriptionTypes'
        db.delete_table('proposal_descriptiontypes')

        # Deleting model 'ProposalTag'
        db.delete_table('proposal_proposaltag')

        # Deleting model 'ProposalDescriptionTag'
        db.delete_table('proposal_proposaldescriptiontag')

        # Adding field 'Proposal.status'
        db.add_column('proposal_proposal', 'status', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Proposal.for_student'
        db.add_column('proposal_proposal', 'for_student', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True), keep_default=False)

        # Adding field 'Proposal.semester'
        db.add_column('proposal_proposal', 'semester', self.gf('django.db.models.fields.CharField')(default='b', max_length=1), keep_default=False)

        # Adding field 'Proposal.student'
        db.add_column('proposal_proposal', 'student', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Proposal.hidden'
        db.add_column('proposal_proposal', 'hidden', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Proposal.description'
        db.add_column('proposal_proposal', 'description', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='proposals_set', to=orm['proposal.ProposalDescription']), keep_default=False)

        # Removing M2M table for field tags on 'Proposal'
        db.delete_table('proposal_proposal_tags')

        # Adding unique constraint on 'Proposal', fields ['name']
        db.create_unique('proposal_proposal', ['name'])

        # Deleting field 'ProposalDescription.lectures'
        db.delete_column('proposal_proposaldescription', 'lectures')

        # Deleting field 'ProposalDescription.ects'
        db.delete_column('proposal_proposaldescription', 'ects')

        # Deleting field 'ProposalDescription.repetitories'
        db.delete_column('proposal_proposaldescription', 'repetitories')

        # Deleting field 'ProposalDescription.seminars'
        db.delete_column('proposal_proposaldescription', 'seminars')

        # Deleting field 'ProposalDescription.exercises'
        db.delete_column('proposal_proposaldescription', 'exercises')

        # Deleting field 'ProposalDescription.laboratories'
        db.delete_column('proposal_proposaldescription', 'laboratories')

        # Adding field 'ProposalDescription.english'
        db.add_column('proposal_proposaldescription', 'english', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'ProposalDescription.type'
        db.add_column('proposal_proposaldescription', 'type', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='descriptionstypes', to=orm['courses.Type']), keep_default=False)

        # Adding field 'ProposalDescription.exam'
        db.add_column('proposal_proposaldescription', 'exam', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Removing M2M table for field tags on 'ProposalDescription'
        db.delete_table('proposal_proposaldescription_tags')

        # Changing field 'ProposalDescription.comments'
        db.alter_column('proposal_proposaldescription', 'comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True))

        # Changing field 'ProposalDescription.date'
        db.alter_column('proposal_proposaldescription', 'date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True))

        # Deleting field 'Book.proposal'
        db.delete_column('proposal_book', 'proposal_id')

        # Adding field 'Book.proposal_description'
        db.add_column('proposal_book', 'proposal_description', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='books', to=orm['proposal.ProposalDescription']), keep_default=False)

        # Changing field 'Book.name'
        db.alter_column('proposal_book', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))
    
    
    def backwards(self, orm):
        
        # Adding model 'DescriptionTypes'
        db.create_table('proposal_descriptiontypes', (
            ('lecture_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descriptionstypes', to=orm['courses.Type'])),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descriptiontypes', to=orm['proposal.ProposalDescription'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('proposal', ['DescriptionTypes'])

        # Adding model 'ProposalTag'
        db.create_table('proposal_proposaltag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal('proposal', ['ProposalTag'])

        # Adding model 'ProposalDescriptionTag'
        db.create_table('proposal_proposaldescriptiontag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal('proposal', ['ProposalDescriptionTag'])

        # Deleting field 'Proposal.status'
        db.delete_column('proposal_proposal', 'status')

        # Deleting field 'Proposal.for_student'
        db.delete_column('proposal_proposal', 'for_student')

        # Deleting field 'Proposal.semester'
        db.delete_column('proposal_proposal', 'semester')

        # Deleting field 'Proposal.student'
        db.delete_column('proposal_proposal', 'student')

        # Deleting field 'Proposal.hidden'
        db.delete_column('proposal_proposal', 'hidden')

        # Deleting field 'Proposal.description'
        db.delete_column('proposal_proposal', 'description_id')

        # Adding M2M table for field tags on 'Proposal'
        db.create_table('proposal_proposal_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proposal', models.ForeignKey(orm['proposal.proposal'], null=False)),
            ('proposaltag', models.ForeignKey(orm['proposal.proposaltag'], null=False))
        ))
        db.create_unique('proposal_proposal_tags', ['proposal_id', 'proposaltag_id'])

        # Removing unique constraint on 'Proposal', fields ['name']
        db.delete_unique('proposal_proposal', ['name'])

        # Adding field 'ProposalDescription.lectures'
        db.add_column('proposal_proposaldescription', 'lectures', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'ProposalDescription.ects'
        db.add_column('proposal_proposaldescription', 'ects', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'ProposalDescription.repetitories'
        db.add_column('proposal_proposaldescription', 'repetitories', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'ProposalDescription.seminars'
        db.add_column('proposal_proposaldescription', 'seminars', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'ProposalDescription.exercises'
        db.add_column('proposal_proposaldescription', 'exercises', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'ProposalDescription.laboratories'
        db.add_column('proposal_proposaldescription', 'laboratories', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Deleting field 'ProposalDescription.english'
        db.delete_column('proposal_proposaldescription', 'english')

        # Deleting field 'ProposalDescription.type'
        db.delete_column('proposal_proposaldescription', 'type_id')

        # Deleting field 'ProposalDescription.exam'
        db.delete_column('proposal_proposaldescription', 'exam')

        # Adding M2M table for field tags on 'ProposalDescription'
        db.create_table('proposal_proposaldescription_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proposaldescription', models.ForeignKey(orm['proposal.proposaldescription'], null=False)),
            ('proposaldescriptiontag', models.ForeignKey(orm['proposal.proposaldescriptiontag'], null=False))
        ))
        db.create_unique('proposal_proposaldescription_tags', ['proposaldescription_id', 'proposaldescriptiontag_id'])

        # Changing field 'ProposalDescription.comments'
        db.alter_column('proposal_proposaldescription', 'comments', self.gf('django.db.models.fields.TextField')(blank=True))

        # Changing field 'ProposalDescription.date'
        db.alter_column('proposal_proposaldescription', 'date', self.gf('django.db.models.fields.DateTimeField')())

        # Adding field 'Book.proposal'
        db.add_column('proposal_book', 'proposal', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='books', to=orm['proposal.Proposal']), keep_default=False)

        # Deleting field 'Book.proposal_description'
        db.delete_column('proposal_book', 'proposal_description_id')

        # Changing field 'Book.name'
        db.alter_column('proposal_book', 'name', self.gf('django.db.models.fields.TextField')())
    
    
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
        'courses.pointtypes': {
            'Meta': {'object_name': 'PointTypes'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'})
        },
        'courses.type': {
            'Meta': {'object_name': 'Type'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Type']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_type': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'short_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5'})
        },
        'proposal.book': {
            'Meta': {'object_name': 'Book'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proposal_description': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'books'", 'to': "orm['proposal.ProposalDescription']"})
        },
        'proposal.proposal': {
            'Meta': {'object_name': 'Proposal'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'proposals_set'", 'to': "orm['proposal.ProposalDescription']"}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Student']", 'symmetrical': 'False', 'blank': 'True'}),
            'for_student': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'helpers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'proposal_helpers_related'", 'blank': 'True', 'to': "orm['users.Employee']"}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'wlasciciel'", 'null': 'True', 'to': "orm['auth.User']"}),
            'semester': ('django.db.models.fields.CharField', [], {'default': "'b'", 'max_length': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'student': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'proposal_teachers_related'", 'blank': 'True', 'to': "orm['users.Employee']"})
        },
        'proposal.proposaldescription': {
            'Meta': {'object_name': 'ProposalDescription'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'autor'", 'to': "orm['auth.User']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'english': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'exam': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descriptions_set'", 'to': "orm['proposal.Proposal']"}),
            'requirements': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descriptionstypes'", 'to': "orm['courses.Type']"}),
            'web_page': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'users.employee': {
            'Meta': {'object_name': 'Employee'},
            'consultations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_news_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 9, 16, 13, 46, 4, 272298)'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'room': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'users.program': {
            'Meta': {'object_name': 'Program'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'type_of_points': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.PointTypes']"})
        },
        'users.student': {
            'Meta': {'object_name': 'Student'},
            'block': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'ects': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_news_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 9, 16, 13, 46, 4, 272298)'}),
            'matricula': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '20'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['users.Program']", 'null': 'True'}),
            'receive_mass_mail_enrollment': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'records_opening_bonus_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'semestr': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }
    
    complete_apps = ['proposal']
