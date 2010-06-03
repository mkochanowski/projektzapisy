import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.core.management import call_command

class Migration(SchemaMigration):
   
    def forwards(self, orm):
        # Deleting field 'Book.order'
        db.delete_column('proposal_book', 'order')

        # Deleting field 'Proposal.lectures'
        db.delete_column('proposal_proposal', 'lectures')

        # Deleting field 'Proposal.laboratories'
        db.delete_column('proposal_proposal', 'laboratories')

        # Deleting field 'Proposal.ects'
        db.delete_column('proposal_proposal', 'ects')

        # Deleting field 'Proposal.exercises'
        db.delete_column('proposal_proposal', 'exercises')

        # Deleting field 'Proposal.repetitories'
        db.delete_column('proposal_proposal', 'repetitories')

        # Deleting field 'Proposal.type'
        db.delete_column('proposal_proposal', 'type')

        # Deleting field 'ProposalDescription.requirements'
        db.delete_column('proposal_proposaldescription', 'requirements')

        # Deleting field 'ProposalDescription.comments'
        db.delete_column('proposal_proposaldescription', 'comments')
    

        # Adding M2M table for field fans on 'Proposal'
        db.create_table('proposal_proposal_fans', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proposal', models.ForeignKey(orm['proposal.proposal'], null=False)),
            ('student', models.ForeignKey(orm['users.student'], null=False))
        ))
        db.create_unique('proposal_proposal_fans', ['proposal_id', 'student_id'])

        # Adding M2M table for field teachers on 'Proposal'
        db.create_table('proposal_proposal_teachers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proposal', models.ForeignKey(orm['proposal.proposal'], null=False)),
            ('employee', models.ForeignKey(orm['users.employee'], null=False))
        ))
        db.create_unique('proposal_proposal_teachers', ['proposal_id', 'employee_id'])
       
        call_command('loaddata', 'offer/proposal/fixtures/fixtures__proposal.json')
   
   
    def backwards(self, orm):
       
        # Removing M2M table for field fans on 'Proposal'
        db.delete_table('proposal_proposal_fans')

        # Removing M2M table for field teachers on 'Proposal'
        db.delete_table('proposal_proposal_teachers')
   
        # Deleting field 'Book.order'
        db.delete_column('proposal_book', 'order')

        # Deleting field 'Proposal.lectures'
        db.delete_column('proposal_proposal', 'lectures')

        # Deleting field 'Proposal.laboratories'
        db.delete_column('proposal_proposal', 'laboratories')

        # Deleting field 'Proposal.ects'
        db.delete_column('proposal_proposal', 'ects')

        # Deleting field 'Proposal.exercises'
        db.delete_column('proposal_proposal', 'exercises')

        # Deleting field 'Proposal.repetitories'
        db.delete_column('proposal_proposal', 'repetitories')

        # Deleting field 'Proposal.type'
        db.delete_column('proposal_proposal', 'type')

        # Deleting field 'ProposalDescription.requirements'
        db.delete_column('proposal_proposaldescription', 'requirements')

        # Deleting field 'ProposalDescription.comments'
        db.delete_column('proposal_proposaldescription', 'comments')

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
        'proposal.book': {
            'Meta': {'object_name': 'Book'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'books'", 'to': "orm['proposal.Proposal']"})
        },
        'proposal.proposal': {
            'Meta': {'object_name': 'Proposal'},
            'ects': ('django.db.models.fields.IntegerField', [], {}),
            'exercises': ('django.db.models.fields.IntegerField', [], {}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Student']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {}),
            'lectures': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repetitories': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['proposal.ProposalTag']", 'blank': 'True'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Employee']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'proposal.proposaldescription': {
            'Meta': {'object_name': 'ProposalDescription'},
            'comments': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descriptions'", 'to': "orm['proposal.Proposal']"}),
            'requirements': ('django.db.models.fields.TextField', [], {}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['proposal.ProposalDescriptionTag']", 'blank': 'True'})
        },
        'proposal.proposaldescriptiontag': {
            'Meta': {'object_name': 'ProposalDescriptionTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'proposal.proposaltag': {
            'Meta': {'object_name': 'ProposalTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'users.employee': {
            'Meta': {'object_name': 'Employee'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'users.student': {
            'Meta': {'object_name': 'Student'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matricula': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '20'}),
            'records_opening_delay_hours': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }
    
    complete_apps = ['proposal']
