# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'Proposal.status'
        db.delete_column('proposal_proposal', 'status')

        # Deleting field 'Proposal.description'
        db.delete_column('proposal_proposal', 'description')

        # Deleting field 'Proposal.deleted'
        db.delete_column('proposal_proposal', 'deleted')

        # Deleting field 'Proposal.slug'
        db.delete_column('proposal_proposal', 'slug')

        # Deleting field 'Proposal.semester'
        db.delete_column('proposal_proposal', 'semester')

        # Deleting field 'Proposal.student'
        db.delete_column('proposal_proposal', 'student')

        # Deleting field 'Proposal.owner'
        db.delete_column('proposal_proposal', 'owner_id')

        # Deleting field 'Proposal.hidden'
        db.delete_column('proposal_proposal', 'hidden')

        # Deleting field 'Proposal.name'
        db.delete_column('proposal_proposal', 'name')

        # Deleting field 'ProposalDescription.requirements'
        db.delete_column('proposal_proposaldescription', 'requirements')

        # Deleting field 'ProposalDescription.exam'
        db.delete_column('proposal_proposaldescription', 'exam')

        # Deleting field 'ProposalDescription.author'
        db.delete_column('proposal_proposaldescription', 'author_id')

        # Deleting field 'ProposalDescription.deleted'
        db.delete_column('proposal_proposaldescription', 'deleted')

        # Deleting field 'ProposalDescription.comments'
        db.delete_column('proposal_proposaldescription', 'comments')

        # Deleting field 'ProposalDescription.web_page'
        db.delete_column('proposal_proposaldescription', 'web_page')

        # Deleting field 'ProposalDescription.english'
        db.delete_column('proposal_proposaldescription', 'english')

        # Deleting field 'ProposalDescription.date'
        db.delete_column('proposal_proposaldescription', 'date')

        # Deleting field 'ProposalDescription.proposal'
        db.delete_column('proposal_proposaldescription', 'proposal_id')

        # Deleting field 'ProposalDescription.type'
        db.delete_column('proposal_proposaldescription', 'type_id')

        # Deleting field 'ProposalDescription.description'
        db.delete_column('proposal_proposaldescription', 'description')
    
    
    def backwards(self, orm):
        
        # Adding field 'Proposal.status'
        db.add_column('proposal_proposal', 'status', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Proposal.description'
        db.add_column('proposal_proposal', 'description', self.gf('django.db.models.fields.TextField')(default=' '), keep_default=False)

        # Adding field 'Proposal.deleted'
        db.add_column('proposal_proposal', 'deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Proposal.slug'
        db.add_column('proposal_proposal', 'slug', self.gf('django.db.models.fields.SlugField')(default=' ', max_length=255, unique=True, db_index=True), keep_default=False)

        # Adding field 'Proposal.semester'
        db.add_column('proposal_proposal', 'semester', self.gf('django.db.models.fields.CharField')(default='b', max_length=1), keep_default=False)

        # Adding field 'Proposal.student'
        db.add_column('proposal_proposal', 'student', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Proposal.owner'
        db.add_column('proposal_proposal', 'owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wlasciciel', null=True, to=orm['auth.User'], blank=True), keep_default=False)

        # Adding field 'Proposal.hidden'
        db.add_column('proposal_proposal', 'hidden', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Proposal.name'
        db.add_column('proposal_proposal', 'name', self.gf('django.db.models.fields.CharField')(default=' ', max_length=255, unique=True), keep_default=False)

        # Adding field 'ProposalDescription.requirements'
        db.add_column('proposal_proposaldescription', 'requirements', self.gf('django.db.models.fields.TextField')(default=' '), keep_default=False)

        # Adding field 'ProposalDescription.exam'
        db.add_column('proposal_proposaldescription', 'exam', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'ProposalDescription.author'
        db.add_column('proposal_proposaldescription', 'author', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='autor', to=orm['auth.User']), keep_default=False)

        # Adding field 'ProposalDescription.deleted'
        db.add_column('proposal_proposaldescription', 'deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'ProposalDescription.comments'
        db.add_column('proposal_proposaldescription', 'comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'ProposalDescription.web_page'
        db.add_column('proposal_proposaldescription', 'web_page', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'ProposalDescription.english'
        db.add_column('proposal_proposaldescription', 'english', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'ProposalDescription.date'
        db.add_column('proposal_proposaldescription', 'date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.date(2012, 5, 22), blank=True), keep_default=False)

        # Adding field 'ProposalDescription.proposal'
        db.add_column('proposal_proposaldescription', 'proposal', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='descriptions_set', to=orm['proposal.Proposal']), keep_default=False)

        # Adding field 'ProposalDescription.type'
        db.add_column('proposal_proposaldescription', 'type', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='descriptionstypes', to=orm['courses.Type']), keep_default=False)

        # Adding field 'ProposalDescription.description'
        db.add_column('proposal_proposaldescription', 'description', self.gf('django.db.models.fields.TextField')(default=' '), keep_default=False)
    
    
    models = {
        'proposal.book': {
            'Meta': {'object_name': 'Book'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proposal_description': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'books'", 'to': "orm['proposal.ProposalDescription']"})
        },
        'proposal.proposal': {
            'Meta': {'object_name': 'Proposal'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'proposal.proposaldescription': {
            'Meta': {'object_name': 'ProposalDescription'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['proposal']
