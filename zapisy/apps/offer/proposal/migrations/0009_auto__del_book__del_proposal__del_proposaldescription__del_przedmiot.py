# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Book'
        db.delete_table('proposal_book')

        # Deleting model 'Proposal'
        db.delete_table('proposal_proposal')

        # Deleting model 'ProposalDescription'
        db.delete_table('proposal_proposaldescription')

        # Deleting model 'Przedmiot'
        db.delete_table('proposal_przedmiot')


    def backwards(self, orm):
        # Adding model 'Book'
        db.create_table('proposal_book', (
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('proposal_description', self.gf('django.db.models.fields.related.ForeignKey')(related_name='books', to=orm['proposal.ProposalDescription'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('proposal', ['Book'])

        # Adding model 'Proposal'
        db.create_table('proposal_proposal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('proposal', ['Proposal'])

        # Adding model 'ProposalDescription'
        db.create_table('proposal_proposaldescription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('proposal', ['ProposalDescription'])

        # Adding model 'Przedmiot'
        db.create_table('proposal_przedmiot', (
            ('rodzaj', self.gf('django.db.models.fields.IntegerField')()),
            ('program', self.gf('django.db.models.fields.TextField')()),
            ('kod_uz', self.gf('django.db.models.fields.IntegerField')()),
            ('wymagania', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('literatura', self.gf('django.db.models.fields.TextField')()),
            ('angielski', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('semestr', self.gf('django.db.models.fields.IntegerField')()),
            ('egzamin', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('opis', self.gf('django.db.models.fields.TextField')()),
            ('rodzaj2007', self.gf('django.db.models.fields.IntegerField')()),
            ('liczba_godzin', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('aktualny', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('nazwa', self.gf('django.db.models.fields.TextField')()),
            ('strona_domowa', self.gf('django.db.models.fields.TextField')()),
            ('punkty2007', self.gf('django.db.models.fields.IntegerField')()),
            ('punkty', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('proposal', ['Przedmiot'])


    models = {
        
    }

    complete_apps = ['proposal']