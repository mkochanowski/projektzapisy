# -*- coding: utf-8 -*-
# Requirements: PyCrypto package version at least 2.3 (pycrypto.org)

################################################################################
##      TODO:                                                                 ##
##                  Napisać skrypt generujący klucze RSA i interfejs do crona ##
##                  tak, by klucze generowały się autoamtycznie na początku   ##
##                  semestru.                                                 ##
################################################################################



from Crypto.PublicKey           import RSA
from itertools                  import product, \
                                       chain, \
                                       combinations
from grade.cryptography.models  import PrivateKey, \
                                       PublicKey, \
                                       GroupsConnection
from enrollment.subjects.models import Group, \
                                       Subject
from django.db.models           import Q

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

def generate_full_connected_groups( sem ):
    subjects    = Subject.objects.filter( semester=sem )
    conn_groups = []
    for sub in subjects:
        groups                = Group.objects.filter( subject = sub ).order_by( 'type' )
        groups_lecture        = groups.filter( type = 1 )
        groups_exercises      = groups.filter( Q( type = 2 ) | Q( type = 4 ))
        groups_labs           = groups.filter( type = 3 )
        groups_labs_exercises = groups.filter( type = 5 )
        groups_seminar        = groups.filter( type = 6 )
        nonempty_groups       = filter( lambda grp: grp, 
                                        [ groups_lecture, \
                                          groups_exercises, \
                                          groups_labs, \
                                          groups_labs_exercises, \
                                          groups_seminar ])        
        conn_groups += list( product( *nonempty_groups ))
    return conn_groups
    
def generate_connected_groups( full_group ):
    member_groups = list( full_group.groups.all() )
    return chain.from_iterable( combinations(member_groups, r) for r in range(1, len( member_groups)+1 ) ) 
        
def save_full_groups(group_list):
    connected_groups = []
    for group in group_list:
        connected_group = GroupsConnection( subject = group[0].subject )
        connected_group.save()
        for el in group:
            connected_group.groups.add( el )
        connected_group.full_connection = connected_group
        connected_groups.append( connected_group )
        connected_group.save()
    return connected_groups
    
def save_subset_groups(groups_map):
    connected_groups = []
    for full_group in groups_map:
        for group in groups_map[ full_group ]:
            sv = GroupsConnection(  subject         = group[0].subject,
                                    full_connection = full_group)
            sv.save()
            for el in group:
                sv.groups.add(el)
            sv.save()
            connected_groups.append(sv)
    return connected_groups
    
def generate_keys_for_groups(group_list):
    pub_list  = []
    priv_list = []
    for el in group_list:
        (pub, priv) = generate_rsa_key()
        pub_list.append(pub)
        priv_list.append(priv)
    return (pub_list, priv_list)
    
def save_public_keys(groups_public_keys):
    for (group, key) in groups_public_keys:
        pkey = PublicKey(   subjects_group = group,
                            public_key_PEM = key)
        pkey.save()
    
def save_private_keys(semester, groups_private_keys):
    for (group, key) in groups_private_keys:
        pkey = PrivateKey(  subjects_group = group,
                            private_key_PEM = key)
        pkey.save()
    
def start_the_grading_protocol( semester ):
    # alt: usuwamy wszystko z "grup"
    # tworzymy nowe grupy jak poniżej, ale bez zapisywania ich listy
    # wybieramy wszystkie grupy połączone i dla każdej tworzymy klucze
    
    # generowanie pełnych grup połączonych - zaw. wszystkie zajęcia do danego przedmiotu
    group_list       = generate_full_connected_groups( semester )    
    connected_groups = save_full_groups( group_list )
    
    # generowanie mniejszych grup
    subset_groups = {}
    for full_connection in connected_groups:
        subset_groups[full_connection] = generate_connected_groups(full_connection)
    connected_groups += save_subset_groups(subset_groups)
    
    # ta część powinna być zmieniona tak, żeby klucze były wygenerowane wcześniej
    # a tu tylko przypisywane / cokolwiek
    (public_keys, private_keys) = generate_keys_for_groups(connected_groups)
    save_public_keys(zip(connected_groups, public_keys))
    save_private_keys(semester, zip(connected_groups, private_keys))
    
