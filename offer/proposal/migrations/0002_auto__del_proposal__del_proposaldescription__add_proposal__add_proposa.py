# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'Proposal'
        db.delete_table('proposal_proposal')

        # Deleting model 'ProposalDescription'
        db.delete_table('proposal_proposaldescription')

        # Adding model 'Proposal'
        db.create_table('proposal_proposal', (
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length = 30)),
            ('ects', self.gf('django.db.models.fields.IntegerField')()),                       
            ('lectures', self.gf('django.db.models.fields.IntegerField')()),
            ('repetitories', self.gf('django.db.models.fields.IntegerField')()),
            ('exercises', self.gf('django.db.models.fields.IntegerField')()),
            ('laboratories', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('proposal', ['Proposal'])

        # Adding M2M table for field tags on 'Proposal'
        db.create_table('proposal_proposal_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proposal', models.ForeignKey(orm['proposal.proposal'], null=False)),
            ('proposaltag', models.ForeignKey(orm['proposal.proposaltag'], null=False))
        ))
        db.create_unique('proposal_proposal_tags', ['proposal_id', 'proposaltag_id'])

        # Adding model 'ProposalDescription'
        db.create_table('proposal_proposaldescription', (
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descriptions', to=orm['proposal.Proposal'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('requirements', self.gf('django.db.models.fields.TextField')()),
            ('comments', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('proposal', ['ProposalDescription'])

        # Adding M2M table for field tags on 'ProposalDescription'
        db.create_table('proposal_proposaldescription_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('proposaldescription', models.ForeignKey(orm['proposal.proposaldescription'], null=False)),
            ('proposaldescriptiontag', models.ForeignKey(orm['proposal.proposaldescriptiontag'], null=False))
        ))
        db.create_unique('proposal_proposaldescription_tags', ['proposaldescription_id', 'proposaldescriptiontag_id'])

        # Adding model 'ProposalTag'
        db.create_table('proposal_proposaltag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('proposal', ['ProposalTag'])

        # Adding model 'ProposalDescriptionTag'
        db.create_table('proposal_proposaldescriptiontag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('proposal', ['ProposalDescriptionTag'])
        
        db.delete_table('proposal_book')
        # Adding model 'Book'
        db.create_table('proposal_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['proposal.Proposal'])),
        ))
        db.send_create_signal('proposal', ['Book'])
    
    
    def backwards(self, orm):
        
        # Adding model 'Proposal'
        db.create_table('proposal_proposal', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('proposal', ['Proposal'])

        # Adding model 'ProposalDescription'
        db.create_table('proposal_proposaldescription', (
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('proposal', self.gf('django.db.models.fields.related.ForeignKey')(related_name='descriptions', to=orm['proposal.Proposal'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('proposal', ['ProposalDescription'])

        # Deleting model 'Proposal'
        db.delete_table('proposal_proposal')

        # Removing M2M table for field tags on 'Proposal'
        db.delete_table('proposal_proposal_tags')

        # Deleting model 'ProposalDescription'
        db.delete_table('proposal_proposaldescription')

        # Removing M2M table for field tags on 'ProposalDescription'
        db.delete_table('proposal_proposaldescription_tags')

        # Deleting model 'ProposalTag'
        db.delete_table('proposal_proposaltag')

        # Deleting model 'ProposalDescriptionTag'
        db.delete_table('proposal_proposaldescriptiontag')
        
        # Deleting model 'Book'
        db.delete_table('proposal_book')        
    
    
    models = {
        'proposal.book': {
            'Meta': {'object_name': 'Book'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'order' : ('django.db.models.fields.IntegerField', [], {}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'books'", 'to': "orm['proposal.Proposal']"})
        },
        'proposal.proposal': {
            'Meta': {'object_name': 'Proposal'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['proposal.ProposalTag']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'ects': ('django.db.models.fields.IntegerField', [], {}),
            
            'lectures': ('django.db.models.fields.IntegerField', [], {}),
            'repetitories': ('django.db.models.fields.IntegerField', [], {}),
            'exercises': ('django.db.models.fields.IntegerField', [], {}),
            'laboratories': ('django.db.models.fields.IntegerField', [], {}),
        },
        'proposal.proposaldescription': {
            'Meta': {'object_name': 'ProposalDescription'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'requirements': ('django.db.models.fields.TextField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proposal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'descriptions'", 'to': "orm['proposal.Proposal']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['proposal.ProposalDescriptionTag']"})
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
        }
    }
    
    complete_apps = ['proposal']
