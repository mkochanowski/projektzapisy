# -*- coding: utf-8 -*-
from Crypto.PublicKey                  import RSA
from Crypto.Random.random              import getrandbits, \
                                              randint
import urllib
import urllib2
import sys
import getpass
import os

RAND_BITS = 512

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


def gcd( a, b ):
    if b > a:
        a, b = b, a
    while a:
            a, b = b%a, a
    return b

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

def generate_sygnature( n , e , m ):
    k   = randint( 2, int(n) )
    while gcd( n, k ) != 1:
        k = randint( 1, int(n) )
        
    a = ( m % n )
    b = expMod( k, e, n )
    t = ( a * b) % n
    
    return (t,k)

def get_url():
    """

    Get server adress from text file

    """
    try:
        file_with_url = open("url.txt","r")
    except IOError, err:
        return u'http://localhost:8000/grade/ticket/client_connection'
    return file_with_url.read() + u'grade/ticket/client_connection'


def send_package(idUser, passwordUser, i, e, n):
    """

    Send keys and get encrypted ticket.
        
    """
    
    m = getrandbits( RAND_BITS )
    
    t,k = generate_sygnature(n,e,m)
    
    values = {
        'idUser'        : idUser,
        'passwordUser'  : passwordUser,
        'groupNumber'    : i,
        'groupKey'       : t
    }

    headers = { 'User-Agent' : 'firefox' }
    
    data = urllib.urlencode(values)

    url = get_url()  
    
    req = urllib2.Request(url, data, headers)
    
    
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, er:
        print er.code
        print er.msg
        print er.headers
        print er.fp.read()
    try:
        st_response = response.read()
        save_result(k, n, m, st_response)
    except ValueError, err:
        print u"nie udało się pobrać klucza."
        print st_response.decode('utf-8')
    except IndexError, err:
        print u"nie udało się pobrać klucza,"
        print st_response.decode('utf-8')

def get_user():
    """

    Enter id and password from keyboard.
        
    """
    
    userId=""
    userPassword=""
    
    userId=raw_input(u"id:")
    userPassword = getpass.getpass()
    
    return userId,userPassword

def save_result(k, n, m, st_response):
    """

    Save a ticket in text file.
    File is appended.
        
    """
    rk  = revMod( k, n )
    sp_response = st_response.split("???")
    st = ((long(sp_response[1]) % n) * (rk % n)) % n
    sp_response[0] = sp_response[0].replace("***",str(m))
    sp_response[0] = sp_response[0].replace("%%%",str(st))
    sp_response[0] = sp_response[0].replace("&#10;","\n")
    file_with_result = open( "tickets.txt", "a" )
    file_with_result.write( sp_response[0] )
    file_with_result.close()
    print u"pobrano bilet: \n" + sp_response[0].decode('utf-8') + u'\n'


def get_key(pollList,sendList):
    """

    Get list of pairs ( poll id, poll public key ) from response and list of chosen polls
        
    """
    
    keys=[]
    
    while len(sendList)>0:
        pos = sendList.pop(0)
        if (int(pos)-1) < len(pollList):
            n,v,k = pollList[int(pos)-1]
            keys.append((n,k))
    return keys

def get_poll_list(idUser, passwordUser):
    """

    Get polls of user.
        
    """
        
    url = get_url() 
    
    
    values = {
        'idUser'        : idUser,
        'passwordUser'  : passwordUser,
        'groupNumber'    : u'*',
        'groupKey'       : u'0'
    }

    headers = { 'User-Agent' : 'firefox' }
    
    data = urllib.urlencode(values)
    
    req = urllib2.Request(url, data, headers)
    
    
    try: response = urllib2.urlopen(req)
    except urllib2.HTTPError, er:
        print er.code
        print er.msg
        print er.headers
        print er.fp.read()

    st = response.read()
    return st

def menu(st):
    """

    Chose poll from list.
    User innterface.
        
    """
    pos = '1'
    poll_list = []
    while int(pos)>0 :
        if os.name == "posix":
                os.system('clear')
        elif os.name in ("nt", "dos", "ce"):
                os.system('CLS')
        i = 1
        for n,v,s in st:
            print i
            i+=1
            print v.decode('utf-8')
            print u"------"
        print u"ankiety do wysłania:"
        choosen_list = u"["
        for p in poll_list:
            choosen_list += unicode(p)+u","
        choosen_list += u"]"
        print choosen_list
        print u"podaj numer ankiety do wysłania"
        print u"u 'nr_ankiety' usuwa numer ankiety z listy"
        print u"(  0 - wysyła dane, -1 - konczy działanie )"
        pos=raw_input()
        try:
            if (len(pos.split(" "))==2) and (pos.split(" ")[0]=='u'):
                pos=pos.split(" ")[1]
                poll_list.remove(int (pos))
            elif int(pos) <= len(st):
                poll_list.append(int(pos))
        except ValueError, err:
            pos='50'
    return poll_list

def to_list(st):
    """

    Convert response to list.
        
    """
    result =[]
    st_l = st.split("\n")
    while len(st_l)>2 :
        nr = st_l.pop(0)
        view = st_l.pop(0)
        key = st_l.pop(0) +"\n"+ st_l.pop(0) +"\n"+ st_l.pop(0) +"\n"+ st_l.pop(0) +"\n"+ st_l.pop(0) +"\n"+ st_l.pop(0)
        result.append((nr,view,RSA.importKey(key)))
    return  result
        
def client():
    """

    Main client function.
        
    """
    
    idUser,passwordUser = get_user()
    pollSt = get_poll_list(idUser, passwordUser)
    
    try:
        x = long(pollSt.split("\n")[0])
    except ValueError, err:
        print u"nie udało się pobrać klucza"
        print pollSt.decode("utf-8")
        return

    pollList = to_list(pollSt)
    sendList = menu(pollList)
    if sendList.pop(len(sendList)-1) == -1:
        print u"Pobieranie biletów zostało anulowane"
        return

    keys = get_key(pollList,sendList)
    
    for nr,key in keys:
        send_package( idUser, passwordUser, nr ,key.e, key.n)

if __name__ == "__main__":
    client()
