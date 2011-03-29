# -*- coding: utf-8 -*- 
import re
import StringIO
import csv
from Crypto.PublicKey                 import RSA
from apps.grade.poll.models         import Poll
from apps.grade.ticket_create.utils import poll_cmp, \
                                             flatten
from apps.enrollment.records.models        import Group


def check_signature( ticket, signed_ticket, public_key ):
    pk = RSA.importKey( public_key.public_key )
    return pk.verify( ticket, (signed_ticket,) )

def group_polls_and_tickets_by_subject( poll_and_ticket_list ):
    if poll_and_ticket_list == []: return []
    
    poll_and_ticket_list.sort( lambda (p1, t1, st1), (p2, t2, st2): poll_cmp( p1, p2 ))
    
    res       = []
    act_polls = []
    act_group = poll_and_ticket_list[ 0 ][ 0 ].group
    
    for ( poll, ticket, signed_ticket ) in poll_and_ticket_list:
        if   not act_group:
            if   poll.group == act_group:
                act_polls.append(( poll.pk, ticket, signed_ticket ))
            else:
                res.append(( u'Ankiety ogólne', act_polls ))
                act_group = poll.group
                act_polls = [( poll.pk, ticket, signed_ticket )]
        else:
            if   poll.group.subject == act_group.subject:
                act_polls.append(( poll.pk, ticket, signed_ticket ))
            else:
                res.append(( unicode( act_group.subject.name ), act_polls ))
                act_group = poll.group
                act_polls = [( poll.pk, ticket, signed_ticket )]
    
    if act_group:
        res.append(( unicode( act_group.subject.name ), act_polls ))
    else:
        res.append(( u'Ankiety ogólne', act_polls ))
        
    return res 
    
def create_slug( name ):
    """
        Creates slug
    """
    if name == u"Ankiety ogólne": return "common"
    
    slug = name.lower()
    slug = re.sub(u'ą', "a", slug)
    slug = re.sub(u'ę', "e", slug)
    slug = re.sub(u'ś', "s", slug)
    slug = re.sub(u'ć', "c", slug)
    slug = re.sub(u'ż', "z", slug)
    slug = re.sub(u'ź', "z", slug)
    slug = re.sub(u'ł', "l", slug)
    slug = re.sub(u'ó', "o", slug)
    slug = re.sub(u'ć', "c", slug)
    slug = re.sub(u'ń', "n", slug)
    slug = re.sub("\W", "-", slug)
    slug = re.sub("-+", "-", slug)
    slug = re.sub("^-", "", slug)
    slug = re.sub("-$", "", slug)
    return slug

def get_polls_for_subject((( sub, slug ), get), groupped_polls ):
    if get:
        return (( sub, slug ), u'jest')
    else:
        return (( sub, slug ), [])

def prepare_data( request, slug ):
    data = { 'errors'   : [], 
             'polls'    : [],
             'finished' : [] }
    
    for id, error in request.session.get( 'errors', default = [] ):
        try:
            p = Poll.objects.get( pk = id )
            data[ 'errors' ].append( "%s: %s" % ( unicode( p ), error ))
        except:
            data[ 'errors' ].append( error )
        
    try:
        del request.session[ 'errors' ]
    except KeyError:
        pass

    polls = request.session.get( "polls", default = [] )
    dict  = {}
    if polls:
        polls_id = reduce(lambda x, y: x + y, map( lambda ((x, s), l): 
                                map( lambda (id, t, st):
                                        id, 
                                    l), polls))    
        for poll in Poll.objects.filter(pk__in=polls_id).select_related('group', 'group__subject', 'group__teacher', 'group__teacher__user'):
            dict[poll.pk] = poll
    
        data[ 'polls' ]    = map( lambda ((x, s), l): 
                                ((x, s),
                                slug==s,
                                map( lambda (id, t, st):
                                        (id, t, st, dict[id].to_url_title( True )), 
                                    l)),
                            polls)
    else:
        data[ 'polls' ] = []
    finished    = request.session.get( "finished", default = [] )
    if finished:
        finished_id = reduce(lambda x, y: x + y, map( lambda ((x, s), l): 
                                map( lambda (id, t, st):
                                        id, 
                                    l), finished))
        for poll in Poll.objects.filter(pk__in=finished_id).select_related('group', 'group__subject', 'group__teacher', 'group__teacher__user'):
            dict[poll.pk] = poll
        
        data[ 'finished' ] = map( lambda ((x, s), l): 
                                ((x, s),
                                slug==s,
                                map( lambda (id, t, st):
                                        (id, t, st, dict[id].to_url_title( True )), 
                                    l)), 
                            finished)
    else:
        data[ 'finished' ] = []
    
    data[ 'finished_polls' ] = len(request.session.get( "finished", default = [] ))
    data[ 'all_polls']  = reduce(lambda x, y: x + y,
                                   map( lambda (p, l): len(l),
                                    request.session.get( "polls", default = [] )), data[ 'finished_polls' ])
    return data

def get_next( poll_list, finished_list, poll_id ):
    ret = False
    for (p_id, t, st, s) in poll_list:
        if ret: return (p_id, t, s)
        ret = p_id == poll_id
    
    ret = False
    for (p_id, t, st, s) in finished_list:
        if ret: return (p_id, t, s)
        ret = p_id == poll_id
        
    return None
    
def get_prev( poll_list, finished_list, poll_id ):
    poll_list.reverse()
    finished_list.reverse()
    
    prev = get_next( poll_list, finished_list, poll_id )
    
    poll_list.reverse()
    finished_list.reverse()
    
    return prev

def get_ticket_and_signed_ticket_from_session( session, slug, poll_id ):
    polls    = session.get( 'polls', default = [])
    finished = session.get( 'finished', default = [])

    polls    = flatten( map(lambda ((n,s), lt): lt, filter( lambda ((name, s), lt): s == slug, polls)))
    finished = flatten( map(lambda ((n,s), lt): lt, filter( lambda ((name, s), lt): s == slug, finished)))
    
    data = polls + finished
    data = map( lambda (id, t, st): (t, st), filter( lambda (id, t, st): id == int( poll_id ), data ))
    
    try:
        return data[0]
    except IndexError:
        return None, None

def getGroups(semester, group = None, type = None, subject = None):
    if subject == -1:
        return {}
    if group:
        return group
    if type:
        if subject:
            groups = Group.objects.filter(type=type, subject=subject)
        else:
            groups = Group.objects.filter(type=type)
    else:
        if subject:
            groups = Group.objects.filter(subject=subject)
        else:
            groups = Group.objects.filter(subject__semester = semester)

    return groups

def poll_cmp_subjects( p1, p2 ):
    if p1.group:
        if p2.group:
            return cmp( p1.group.subject.name, p2.group.subject.name )
        else:
            return 1
    else:
        return -1

def poll_cmp_teachers( p1, p2 ):
    if p1.group:
        if p2.group:
            return cmp( p1.group.get_teacher_full_name(), p2.group.get_teacher_full_name() )
        else:
            return 1
    else:
        return -1
        
def group_polls_by_subject( polls ):
    polls.sort( poll_cmp_subjects )
    
    groupped = []
    if polls:
        try:
            act_sub = polls[ 0 ].group.subject.name
        except:
            act_sub = u"Ankiety ogólne"
        act = [ polls[ 0 ]]
        polls = polls[ 1: ]
        
        for poll in polls:
            try:
                sub = poll.group.subject.name
            except:
                sub = u"Ankiety ogólne"
            
            if sub == act_sub:
                act.append( poll )
            else:
                groupped.append(( act_sub, act ))
                act     = [ poll ]
                act_sub = sub
        if act: groupped.append(( act_sub, act ))
    return groupped
            
    
def group_polls_by_teacher( polls ):
    polls.sort( poll_cmp_teachers )

    groupped = []
    if polls:
        try:
            act_sub = polls[ 0 ].group.get_teacher_full_name()
        except:
            act_sub = u"Ankiety ogólne"
        act = [ polls[ 0 ]]
        polls = polls[ 1: ]
        
        for poll in polls:
            try:
                sub = poll.group.get_teacher_full_name()
            except:
                sub = u"Ankiety ogólne"
            
            if sub == act_sub:
                act.append( poll )
            else:
                groupped.append(( act_sub, act ))
                act     = [ poll ]
                act_sub = sub
        if act: groupped.append(( act_sub, act ))
    return groupped

def declination_poll(num, nominative = False):
    if num == 1:
        if nominative:
            return u'ankieta'
        else:        
            return u'ankietę'
    if ((num % 10) in [2,3,4] and (num < 10 or num > 20)):
        return u'ankiety'
    return u'ankiet'
    

def declination_section(num, nominative = False):
    if num == 1:
        if nominative:
            return u'sekcja'
        else:
            return u'sekcję'
    if ((num % 10) in [2,3,4] and (num < 10 or num > 20)):
        return u'sekcje'
    return u'sekcji'
    
####  HELPER FOR UNICODE + CSV -- Python's CSV does not support unicode 

class UnicodeWriter(object):

    def __init__(self, f, dialect=csv.excel_tab, encoding="utf-16", **kwds):
        # Redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoding = encoding
    
    def writerow(self, row):
        # Modified from original: now using unicode(s) to deal with e.g. ints
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = data.encode(self.encoding)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
    
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
            
#### CSV file preparation

def generate_csv_title(poll):
    res = poll.title
    try:        
        res += u' ' + poll.group.subject.name
        res += u' ' + poll.group.get_type_display()
        res += u' ' + poll.group.get_teacher_full_name()
    except:
        res += u' ' + u'Ankieta ogólna'
    res += u' ' + unicode(poll.pk)
    res += u'.csv'
    return unicode(res)
    
def csv_prepare_header(sections):
    """
    csv_prepare_header prepares header for a specific poll - that is, it provides 
    questions for the specific poll, prepared as reqired by the csv.writer
    """
    row = []
    for sec_questions in sections:        
        row += sec_questions
    return row
    
def csv_prepare(handle, poll_sections, poll_data):
    """
    csv_prepare prepares the entire csv file - typically this is a file for
    a specific poll
    """
    #handle = StringIO.StringIO() #open(csv_title, 'wb')
    writer = UnicodeWriter(handle, delimiter=';', quotechar='"', quoting = csv.QUOTE_ALL)    
    writer.writerow( csv_prepare_header(poll_sections) )    
    for poll in poll_data:
        writer.writerow(poll)    
    return handle
    
