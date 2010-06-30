# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'DescriptionTypes'
        db.create_table('proposal_descriptiontypes', (
            ('study_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descriptions', to=orm['users.Type'])),
            ('lecture_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descriptions', to=orm['proposal.Types'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.related.ForeignKey')(related_name='types', to=orm['proposal.Proposal'])),
        ))
        db.send_create_signal('proposal', ['DescriptionTypes'])

        # Adding model 'Types'
        db.create_table('proposal_types', (
            ('meta_type', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['proposal.Types'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('proposal', ['Types'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'DescriptionTypes'
        db.delete_table('proposal_descriptiontypes')

        # Deleting model 'Types'
        db.delete_table('proposal_types')
    
    
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
        'proposal.descriptiontypes': {
            'Meta': {'object_name': 'DescriptionTypes'},
            'description': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'types'", 'to': "orm['proposal.Proposal']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lecture_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descriptions'", 'to': "orm['proposal.Types']"}),
            'study_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descriptions'", 'to': "orm['users.Type']"})
        },
        'proposal.proposal': {
            'Meta': {'object_name': 'Proposal'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'fans': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['users.Student']", 'blank': 'True'}),
            'helpers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'proposal_helpers_related'", 'blank': 'True', 'to': "orm['users.Employee']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'wlasciciel'", 'null': 'True', 'to': "orm['auth.User']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['proposal.ProposalTag']", 'blank': 'True'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'proposal_teachers_related'", 'blank': 'True', 'to': "orm['users.Employee']"})
        },
        'proposal.proposaldescription': {
            'Meta': {'object_name': 'ProposalDescription'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'autor'", 'to': "orm['auth.User']"}),
            'comments': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'ects': ('django.db.models.fields.IntegerField', [], {}),
            'exercises': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {}),
            'lectures': ('django.db.models.fields.IntegerField', [], {}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descriptions'", 'to': "orm['proposal.Proposal']"}),
            'repetitories': ('django.db.models.fields.IntegerField', [], {}),
            'requirements': ('django.db.models.fields.TextField', [], {}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['proposal.ProposalDescriptionTag']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'web_page': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
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
        'proposal.types': {
            'Meta': {'object_name': 'Types'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proposal.Types']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta_type': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'users.employee': {
            'Meta': {'object_name': 'Employee'},
            'consultations': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receive_mass_mail_offer': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'users.student': {
            'Meta': {'object_name': 'Student'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matricula': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '20'}),
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
    
    complete_apps = ['proposal']
