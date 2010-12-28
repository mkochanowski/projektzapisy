# -*- coding: utf-8 -*-
from Crypto.PublicKey                  import RSA
from Crypto.Random.random              import getrandbits, \
                                              randint
from itertools                         import product
from django.db.models                  import Q

from fereol.enrollment.subjects.models import Subject, \
                                              Group
                                              
from fereol.enrollment.records.models  import Record 

from fereol.grade.ticket_create.models import PublicKey, \
                                              PrivateKey, \
                                              UsedTicketStamp 

from fereol.grade.ticket_create.exceptions import *

from django.utils.safestring           import SafeUnicode

RAND_BITS = 512 

def gcd( a, b ):
        if b > a:
            a, b = b, a
        while a:
                a, b = b%a, a
        return b
      
def gcwd( u, v ):
	u1 = 1
	u2 = 0
	u3 = u
	v1 = 0
	v2 = 1
	v3 = v
	while v3 != 0:
		q = u3 / v3
		t1 = u1 - q * v1
		t2 = u2 - q * v2
		t3 = u3 - q * v3
		u1 = v1
		u2 = v2
		u3 = v3
		v1 = t1
		v2 = t2
		v3 = t3
	return u1, u2, u3
    
def expMod( a, b, q ):
    p = 1
    
    while b > 0:
        if b & 1:
            p = (p * a) % q
        a = (a * a) % q
        b /= 2
    return p
            
def revMod( a, m ):
    x, y, d = gcwd( a, m )
    
    if d != 1: return -1
    
    x %= m
    if x < 0: x += m
    return x
    
         
def generate_rsa_key():
    """ 
        Generates RSA key - that is, a pair (public key, private key)
        both exported in PEM format 
    """
    key_length = 2048
    RSAkey     = RSA.generate(key_length)
    privateKey = RSAkey.exportKey()
    publicKey  = RSAkey.publickey().exportKey()
    return (publicKey, privateKey)
    
def save_public_keys(groups_public_keys):
    for (group, key) in groups_public_keys:
        pkey = PublicKey(   group = group,
                            public_key_PEM = key)
        pkey.save()
    
def save_private_keys(groups_private_keys):
    for (group, key) in groups_private_keys:
        pkey = PrivateKey(  group = group,
                            private_key_PEM = key)
        pkey.save()

def generate_keys_for_groups( sem ):
    group_list = Group.objects.filter( subject__semester = sem )
    pub_list  = []
    priv_list = []
    for el in group_list:
        (pub, priv) = generate_rsa_key()
        pub_list.append(pub)
        priv_list.append(priv)
    save_public_keys(zip(group_list, pub_list))
    save_private_keys(zip(group_list, priv_list))
    return 
def split_groups_by_subject( group_list ):
    if group_list == []: return []
    res       = []
    act_groups =[]
    act_sub    = group_list[ 0 ].subject
    
    for group in group_list:
        if group.subject == act_sub:
           act_groups.append( group )
        else:
            res.append( act_groups )
            act_groups = [ group ]
            act_sub    = group.subject
    
    res.append( act_groups )
    return res

def generate_ticket( group_list ):
    ## TODO: Docelowo ma być po stronie przeglądarki
    m       = getrandbits( RAND_BITS )
    blinded = []
    
    for group in group_list:
        key =  RSA.importKey( PublicKey.objects.get( group = group ).public_key_PEM )
        n   = key.n
        e   = key.e
        k   = randint( 2, n )
        while gcd( n, k ) != 1:
            k = randint( 1, n )
        
        a = ( m % n )
        b = expMod( k, e, n )
        t = ( a * b) % n
        
        blinded.append(( group, t, (m, k) ))
    return blinded
    
def check_group_assignment( user, group ):
    ## TODO: zapisany, a nie oczekujący; grupy z tego semestru
    r = Record.objects.get( group = group, student = user.student )
    if not r: raise InvalidGroupException
    
def check_ticket_not_signed( user, group ):
    ## TODO: obecny semestr
    u = UsedTicketStamp.objects.filter( student = user.student, group = group )
    if u: raise TicketUsed
    
def find_rsa_private_key( group ):
    """ 
        Returns RSAobj object for specified group; if no such group is
        found within the system, throws an error 
    """
    rsa_private = PrivateKey.objects.get( group = group ).private_key_PEM
    RSAImpl     = RSA.RSAImplementation()
    return RSAImpl.importKey( rsa_private )
    
def sign_ticket( ticket, key ):
    return key.sign( ticket, 0 )
    
def mark_group_used( user, group ):
    ## TODO: dodać semestr
    u = UsedTicketStamp( student = user.student,
                         group   = group )
    u.save()
    
def ticket_check_and_sign( user, group, ticket ):
    check_group_assignment( user, group )
    check_ticket_not_signed( user, group )
    key    = find_rsa_private_key( group )
    signed = sign_ticket( ticket, key )
    mark_group_used( user, group )
    return signed

def secure_signer( user, g, t ):
    try:
        return ticket_check_and_sign( user, g, t ), 
    except InvalidGroupException:
        return u"Nie jesteś zapisany do tej grupy",
    except TicketUsed:
        return u"Bilet już pobrano",

def unblind( group, st, k ):
    # TODO: To ma być po stronie przeglądarki 
    st  = st[0]
    if   st == u"Nie jesteś zapisany do tej grupy":
        return st
    elif st == u"Bilet już pobrano":
        return st
    else:
        st  = st[0]
        key =  RSA.importKey( PublicKey.objects.get( group = group ).public_key_PEM )
        n   = key.n
        rk  = revMod( k, n )
        return ((st % n) * (rk % n)) % n
        
def get_valid_tickets( tl ):
    err = []
    val = []
    for g, t, st in tl:
        if st == u"Nie jesteś zapisany do tej grupy" or \
           st == u"Bilet już pobrano":
                err.append(( g, st ))
        else:
                val.append(( g, t, st ))
    
    return err, val
        
def to_plaintext( vtl ):
    res = ""
    for g, t, st in vtl:
        res += g.subject.name + " &#10; "
        res += g.get_type_display() + ": " + g.get_teacher_full_name() + " &#10; "
        res += unicode( t ) + " &#10; "
        res += unicode( st ) + " &#10; "
        res += "---------------------------------- &#10; "
    return SafeUnicode( res )
