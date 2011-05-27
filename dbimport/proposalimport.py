# -*- coding: utf-8 -*-

FEREOL_PATH = '../..'

import sys
import os
from django.core.management import setup_environ
from datetime import time

if __name__ == '__main__':
    sys.path.append(FEREOL_PATH)
    sys.path.append(FEREOL_PATH + '/fereol')
    from fereol import settings
    setup_environ(settings)

import psycopg2 as pg
import psycopg2.extensions

from apps.enrollment.records.models import Record
from apps.offer.proposal.models import Proposal, ProposalTag, ProposalDescription

from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db import transaction

from datetime import datetime, date
import re



def import_proposal(conn):
    cur = conn.cursor()
    cur.execute('select nazwa, egzamin, semestr, opis, wymagania, punkty from przedmiot')

    summer = ProposalTag.objects.get_or_create(name="summer")[0]  
    winter = ProposalTag.objects.get_or_create(name="winter")[0] 
    exam = ProposalTag.objects.get_or_create(name="exam")[0]
    offer = ProposalTag.objects.get_or_create(name="offer")[0]
    vote = ProposalTag.objects.get_or_create(name="vote")[0]  
   
    author = User.objects.filter(username="gosia")[0]

    for r in cur:
        try:
            p = Proposal.objects.get_or_create(name = r[0], slug = slugify(r[0]))[0]
            p.tags.add(vote)
            p.tags.add(offer)
            if r[1]:
                p.tags.add(exam)
            if r[2]==1:
                p.tags.add(winter)
            elif r[2]==2:
                p.tags.add(summer)
            p.save

            d = ProposalDescription.objects.get_or_create(proposal = p,
                                                          description = r[3],
                                                          requirements = r[4],
                                                          comments = '',
                                                          date = date.today(),
                                                          author = author,
                                                          ects = r[5],
                                                          lectures = 0,
                                                          repetitories = 0,
                                                          seminars = 0,
                                                          exercises = 0,
                                                          laboratories = 0)
        except:
            print r[0]
            pass
def proposalimport():  
 
    conn = pg.connect('dbname=oferta09 user=fereol password=fereol host=localhost port=5432')

    import_proposal(conn)

    conn.close()


proposalimport()
