# -*- coding: utf-8 -*-
from Crypto.PublicKey                  import RSA
from Crypto.Random.random              import getrandbits, \
                                              randint
import urllib
import urllib2
import sys



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
    file_with_url = open("url.txt","r")
    return file_with_url.read()


def send_package(idUser, passwordUser, i, e, n, m = getrandbits( RAND_BITS ) ):
    
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
        print "nie udało się pobrać klucza"
        print st_response
    except IndexError, err:
        print "nie udało się pobrać klucza"
        print st_response

def save_result(k, n, m, st_response):
    rk  = revMod( k, n )
    sp_response = (st_response).split(" &#10;")
    last = sp_response.pop()
    st = ((long(last) % n) * (rk % n)) % n
    w = ""
    for txt in sp_response:
        w += txt + " \n"
    file_with_result = open("wynik.txt","w")
    file_with_result.write(w + str(m) + " \n" + str(st) + " \n---------------------------------- \n")
    file_with_result.close()


def get_key():
    file_with_key = open("klucz.txt","r")
    file_string = file_with_key.read()
    
    begin_string = file_string[:26]
    key_string = file_string[26:(len(file_string)-24)]
    end_string = file_string[(len(file_string)-24):]
    
    key_string = key_string.replace(" ","\n")

    key = RSA.importKey (begin_string+key_string+end_string)
    
    file_with_key.close()
    
    return key

def client(idUser, passwordUser, nr):
    key = get_key()
    send_package( idUser, passwordUser, nr ,key.e, key.n)

if __name__ == "__main__":
     client( sys.argv[1], sys.argv[2], sys.argv[3])
