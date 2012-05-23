# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Przedmiot'
        db.create_table('proposal_przedmiot', (
            ('rodzaj', self.gf('django.db.models.fields.IntegerField')()),
            ('rodzaj2007', self.gf('django.db.models.fields.IntegerField')()),
            ('kod_uz', self.gf('django.db.models.fields.IntegerField')()),
            ('wymagania', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('literatura', self.gf('django.db.models.fields.TextField')()),
            ('angielski', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('semestr', self.gf('django.db.models.fields.IntegerField')()),
            ('egzamin', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('strona_domowa', self.gf('django.db.models.fields.TextField')()),
            ('opis', self.gf('django.db.models.fields.TextField')()),
            ('liczba_godzin', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('aktualny', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('program', self.gf('django.db.models.fields.TextField')()),
            ('nazwa', self.gf('django.db.models.fields.TextField')()),
            ('punkty2007', self.gf('django.db.models.fields.IntegerField')()),
            ('punkty', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('proposal', ['Przedmiot'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Przedmiot'
        db.delete_table('proposal_przedmiot')
    
    
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
        },
        'proposal.przedmiot': {
            'Meta': {'object_name': 'Przedmiot'},
            'aktualny': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'angielski': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'egzamin': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kod_uz': ('django.db.models.fields.IntegerField', [], {}),
            'liczba_godzin': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'literatura': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'nazwa': ('django.db.models.fields.TextField', [], {}),
            'opis': ('django.db.models.fields.TextField', [], {}),
            'program': ('django.db.models.fields.TextField', [], {}),
            'punkty': ('django.db.models.fields.IntegerField', [], {}),
            'punkty2007': ('django.db.models.fields.IntegerField', [], {}),
            'rodzaj': ('django.db.models.fields.IntegerField', [], {}),
            'rodzaj2007': ('django.db.models.fields.IntegerField', [], {}),
            'semestr': ('django.db.models.fields.IntegerField', [], {}),
            'strona_domowa': ('django.db.models.fields.TextField', [], {}),
            'wymagania': ('django.db.models.fields.TextField', [], {})
        }
    }
    
    complete_apps = ['proposal']
