# -*- coding: utf-8 -*- 
from Crypto.PublicKey         import RSA
from fereol.grade.poll.models import Poll

def check_signature( ticket, signed_ticket, public_key ):
    pk = RSA.importKey( public_key.public_key )
    return pk.verify( ticket, (signed_ticket,) )

def prepare_data( request ):
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
	   
    data[ 'polls' ]    = request.session.get( 'polls', default = [] )
    data[ 'finished' ] = request.session.get( 'finished', default = [] )
    
    data[ 'polls' ] = map( lambda (id, t): 
                                (id, t, Poll.objects.get( pk = id ).to_url_title( True )), 
                           data[ 'polls' ])
    data[ 'finished' ] = map( lambda (id, t): 
                                (id, t, Poll.objects.get( pk = id ).to_url_title( True )), 
                              data[ 'finished' ])
    return data
