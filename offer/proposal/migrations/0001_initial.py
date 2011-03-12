# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Proposal'
        db.create_table('proposal_proposal', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)), # primary key jest tworzone automatycznie!
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length = 30)),
            ('ects', self.gf('django.db.models.fields.IntegerField')()),                       
            ('lectures', self.gf('django.db.models.fields.IntegerField')()),
            ('repetitories', self.gf('django.db.models.fields.IntegerField')()),
            ('exercises', self.gf('django.db.models.fields.IntegerField')()),
            ('laboratories', self.gf('django.db.models.fields.IntegerField')()),                  
        ))
        db.send_create_signal('proposal', ['Proposal'])

        # Adding model 'ProposalDescription'
        db.create_table('proposal_proposaldescription', (
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('requirements', self.gf('django.db.models.fields.TextField')()),
            ('comments', self.gf('django.db.models.fields.TextField')()),               
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descriptions', to=orm['proposal.Proposal'])),
        ))
        db.send_create_signal('proposal', ['ProposalDescription'])

        # Adding model 'Book'
        db.create_table('proposal_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['proposal.Proposal'])),
        ))
        db.send_create_signal('proposal', ['Book'])
        
    def backwards(self, orm):
        
        # Deleting model 'Proposal'
        db.delete_table('proposal_proposal')

        # Deleting model 'ProposalDescription'
        db.delete_table('proposal_proposaldescription')

        # Deleting model 'Book'
        db.delete_table('proposal_book')
    
    
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
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proposal.Proposal']"})
        },
        'proposal.Proposal': {
            'Meta': {'object_name': 'Proposal'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'ects': ('django.db.models.fields.IntegerField', [], {}),
            
            'lectures': ('django.db.models.fields.IntegerField', [], {}),
            'repetitories': ('django.db.models.fields.IntegerField', [], {}),
            'exercises': ('django.db.models.fields.IntegerField', [], {}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {}),                        
        },
        'proposal.Proposaldescription': {
            'Meta': {'object_name': 'ProposalDescription'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'requirements': ('django.db.models.fields.TextField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {}),            
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descriptions'", 'to': "orm['proposal.Proposal']"})
        },
    }
    
    complete_apps = ['proposal']

