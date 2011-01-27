# -*- coding: utf-8 -*- 
import re
from Crypto.PublicKey                 import RSA
from fereol.grade.poll.models         import Poll
from fereol.grade.ticket_create.utils import poll_cmp, \
                                             flatten

def check_enable_grade():
    if Poll.get_polls_for_semester():
        if Poll.get_current_semester_polls_without_keys():
            return False
        return True
    else:
        return False

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
    
    data[ 'polls' ]    = map( lambda ((x, s), l): 
                                ((x, s), 
                                slug==s, 
                                map( lambda (id, t, st):
                                        (id, t, st, Poll.objects.get( pk = id ).to_url_title( True )), 
                                    l)),
                            request.session.get( "polls", default = [] ))
    data[ 'finished' ] = map( lambda ((x, s), l): 
                                ((x, s), 
                                slug==s, 
                                map( lambda (id, t, st):
                                        (id, t, st, Poll.objects.get( pk = id ).to_url_title( True )), 
                                    l)), 
                            request.session.get( "finished", default = [] ))
    
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
