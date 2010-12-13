# -*- coding: utf-8 -*-
# Requirements: PyCrypto package version at least 2.3 (pycrypto.org)
from Crypto.PublicKey                     import RSA
from Crypto.Random.random                 import getrandbits, \
                                                 randint
from fereol.grade.cryptography.models     import GroupsConnection, \
                                                 PublicKey, \
                                                 PrivateKey
from fereol.grade.signature_server.models import UsedTicketStamp
from fereol.enrollment.records.models     import Record

RAND_BITS = 512

def gcd( a, b ):
        if b > a:
            a, b = b, a
        while a:
                a, b = b%a, a
        return b

def generate_ticket( user, groups_connection ):
    public_key = RSA.importKey( PublicKey.objects.get( subjects_group = groups_connection ).public_key_PEM )
    n = public_key.n
    e = public_key.e
    m = getrandbits( RAND_BITS )
    k = 1
    while gcd( n, k ) != 1:
        k = randint( 1, n )
    t = (m * (k ** e)) % n
    return ( groups_connection.pk, t )
    
def compare_group_lists( gl1, gl2 ):
    return cmp( gl1[ 0 ].subject.slug, gl2[ 0 ].subject.slug )

def group_groups_by_subject( group_list ):
    groups          = []
    current_groups  = []
    current_subject = group_list[ 0 ].subject.slug
    for g in group_list:
        if g.subject.slug != current_subject:
            groups.append( current_groups )
            current_groups  = [ g ]
            current_subject = g.subject.slug
        else: 
            current_groups.append( g )
    groups.append( current_groups )
    groups.sort( compare_group_lists )
    return groups

def prepare_groups( group_list ):
    sorted   = group_groups_by_subject( group_list )
    prepared = {}
    for gl in sorted:
        prepared[ gl[0].subject.name ] = gl
    return prepared

def group_list_to_group_connection( group_list ):
    ############################################################################
    ##              TODO:                                                     ##
    ##                      Efektywniejsza implementacja                      ##
    ############################################################################
    gcs = GroupsConnection.objects.all()
    for gc in gcs:
        if set( gc.groups.all()) == set( group_list ):
            return gc
    
def sign_ticket(ticket, rsaKey):
    return rsaKey.sign( ticket, 0 )

def find_rsa_private_key( group ):
    """ 
        Returns RSAobj object for specified group; if no such group is
        found within the system, throws an error 
    """
    rsa_private = PrivateKey.objects.get( subjects_group = group ).private_key_PEM
    RSAImpl     = RSA.RSAImplementation()
    return RSAImpl.importKey( rsa_private )
    
def mark_user_group_used( user, group ):
    """ 
        Marks group and all groups connected with it as used for
        specified user; 
        returns "ok" 
    """
    group_connection = GroupsConnection.objects.get( pk = group )
    used_groups      = group_connection.groups.all()
    full_connection  = GroupsConnection.objects.get( pk = group_connection.full_connection.pk )
    connected_groups = GroupsConnection.objects.filter( full_connection = full_connection.pk )
    #filtrowanie - chcemy tylko conn_groups, które zaw. coś z used_groups
    ############################################################################
    ##          TODO:                                                         ##
    ##                      Lepsza implementacja                              ##
    ############################################################################
    connected_filtered = []
    for cg in connected_groups:
        groups = list( cg.groups.all())
        for ug in used_groups:
            if ug in groups:
                connected_filtered.append( cg )
                break
                
    for group in connected_filtered:
        u = UsedTicketStamp( student           = user.student, 
                             groups_connection = group )
        u.save()
        #dodać semestr..
    return 1

def check_group_assignment( user, group ):
    """ 
        Throws an error when user is not assigned to the group;
        otherwise returns "ok" 
    """
    
    #pobieramy wszystkie grupy będące w połączeniu"
    groups = GroupsConnection.objects.get( pk = group ).groups.all()
    for g in groups:        
        r = Record.objects.get( group = g, student = user.student )
        if not r:
            return 0
    return 1
    
def check_ticket_not_signed(user, group):
    """ 
        Throws an error when user has already used his right to
        obtain one ticket for specified group;
        otherwise returns "ok"
    """
    # powinno być jeszcze semester = current, ale dużo z tym zachodu
    u = UsedTicketStamp.objects.filter( student = user, groups_connection = group )
    if u:
        return 0
    return 1

def check_and_sign(user, group, ticket):
    """ 
        Assume user is authenticated; check whether user is allowed to
        obtain signature under the ticket for the group;
        sign the ticket;
        mark group as used;
        return pair (ticket, signed ticket) 
    """  
    check_group_assignment( user, group )
    check_ticket_not_signed( user, group )
    rsaKey = find_rsa_private_key( group )
    signed = sign_ticket( ticket, rsaKey )
    mark_user_group_used( user, group )
    return signed

def signature_preparer( user, list_of_data ):
    groups         = [] 
    tickets        = [] 
    signed_tickets = []
    for group_pk, ticket in list_of_data:
        groups.append(         GroupsConnection.objects.get( pk = group_pk ))
        tickets.append(        ticket )
        signed_tickets.append( check_and_sign( user, group_pk, ticket ))
    return zip( groups, tickets, signed_tickets )
