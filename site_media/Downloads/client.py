# -*- coding: utf-8 -*-
########################################################################
#                   Fereol poll keys download client                   #
#                     downloaded from www.fereol.pl                    #
########################################################################
#   written in python 2.7  
# If you would like to redirect your output to file please set
# PYTHONIOENCODING environment variable to utf-8

# moduł do kodowania 
from Crypto.PublicKey                  import RSA
from Crypto.Random.random              import getrandbits, \
                                              randint
# moduły do komunikacji sieciowej
import urllib
import urllib2

# moduły pomocnicze
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

def generate_signature( n , e , m ):
    k   = randint( 2, int(n) )
    while gcd( n, k ) != 1:
        k = randint( 1, int(n) )
        
    a = ( m % n )
    b = expMod( k, e, n )
    t = ( a * b) % n
    
    return (t,k)

def get_url():
    """

    Get server adress from text file. Default value is http://localhost:8000/

    """

    # pobieranie adresu serwera. Jeżeli plik z adresem nie istnieje podawana jest wartość domyślna
    # TODO:
    #   przerobić tak, żeby domyślnie tu był adres fereola i nie dawać możliwości zmiany
    try:
        file_with_url = open("url.txt","r")
    except IOError, err:
        return u'http://localhost:8000/grade/ticket/client_connection'
    return file_with_url.read() + u'grade/ticket/client_connection'


def send_package(idUser, passwordUser, i, e, n, m ):
    """

    Send keys and get encrypted ticket.
        
    """
    
    # zakodowywanie kluczy do ankiet za pomocą m
    t,k = generate_signature(n,e,m)

    # dane do przesłania na serwer
    values = {
        'idUser'        : idUser,
        'passwordUser'  : passwordUser,
        'groupNumber'   : i,
        'groupKey'      : t
    }

    headers = { 'User-Agent' : 'firefox' }
    
    data = urllib.urlencode(values)

    # pobieranie adresu serwera ( z pliku url.txt )
    url = get_url()  

    # wysyłania zapytania na serwer
    req = urllib2.Request(url, data, headers)
  
    # odbieranie i analiza odpowiedzi serwera
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, er:
        print er.code.encode('utf-8')
        print er.msg.encode('utf-8')
        print er.headers.encode('utf-8')
        print er.fp.read().encode('utf-8')

    # zapisywanie wyników
    try:
        st_response = response.read()
        save_result(k, n, m, st_response)
    except ValueError, err:
        print u"nie udało się pobrać biletu".encode('utf-8')
        print st_response.decode('utf-8').encode('utf-8')
    except IndexError, err:
        print u"nie udało się pobrać biletu".encode('utf-8')
        print st_response.decode('utf-8').encode('utf-8')

def get_user():
    """

    Enter id and password from keyboard.
        
    """
    # pobieranie danych o użytkowniku z klawiatury
    user = raw_input("Nazwa użytkownika [%s]: " % getpass.getuser())
    if not user:
        user = getpass.getuser()

    if sys.stdin.isatty():
        password = getpass.getpass('Hasło: ')
    else:
        password = sys.stdin.readline().rstrip()

    return user, password
    
def save_result(k, n, m, st_response):
    """

    Save a ticket in text file.
    File is appended.
        
    """

    
    # dzielenie odpowiedzi serwera
    sp_response = st_response.split("???")

    # odkodowywanie biletu
    rk  = revMod( k, n )
    st = ((long(sp_response[1]) % n) * (rk % n)) % n

    # zapisywanie odkodowanych biletów
    sp_response[0] = sp_response[0].replace("***",str(m))
    sp_response[0] = sp_response[0].replace("%%%",str(st))
    sp_response[0] = sp_response[0].replace("&#10;","\n")

    # dopisywanie biletów do pliku tickets.txt
    file_with_result = open( "tickets.txt", "a" )
    file_with_result.write( sp_response[0] )
    file_with_result.close()
    # wyświetlanie informacji, że pobieranie biletu zakończyło się sukcesem
    print (u"pobrano bilet: \n" + sp_response[0].decode('utf-8') + u'\n').encode('utf-8')


def get_key(pollList,sendList):
    """

    Get list of pairs ( poll id, poll public key ) from response and list of chosen polls
        
    """

    # wybieranie kluczy publicznych do ankiet wybranych przez użytkownika w funkcji menu(st)
    
    keys=[]

    for p in sendList:
        if p.split('.')[1]=='0':
            # wersja dla ankiet powiązanych
            m = getrandbits( RAND_BITS )
            for s in pollList[int(p.split('.')[0])-1]:
                n,v,k = s
                keys.append((n,m,k))
        else:
            # wersja dla ankiet powiązanych
            n,v,k = pollList[int(p.split('.')[0])-1][int(p.split('.')[1])-1]
            m = getrandbits( RAND_BITS )
            keys.append((n,m,k))

    return keys

def get_poll_list(idUser, passwordUser):
    """

    Get polls of user.
        
    """

    # pobieranie adresu serwera ( z pliku url.txt )
    url = get_url() 
    
    # dane do przesłania na serwer
    values = {
        'idUser'        : idUser,
        'passwordUser'  : passwordUser,
        'groupNumber'    : u'*',
        'groupKey'       : u'0'
    }

    headers = { 'User-Agent' : 'firefox' }

    # kodowanie danych
    data = urllib.urlencode(values)

    # przesyłanie zapytania na serwer
    req = urllib2.Request(url, data, headers)
    

    # analiza odpowiedzi serwera
    try: response = urllib2.urlopen(req)
    except urllib2.HTTPError, er:
        print er.code.encode('utf-8')
        print er.msg.encode('utf-8')
        print er.headers.encode('utf-8')
        print er.fp.read().encode('utf-8')

    st = response.read()
    return st

def menu(st_m):
    """

    Chose poll from list.
    User interface.
        
    """

    # menu użytkownika do wybierania ankiet

    # lista poprawnych danych wejściowych, aktualizowana podczas działania programu    
    good_res=['0','-1']

    # zmienna przechowująca polecenie użytkownika
    pos = '1'

    # lista ankiet do wysłania
    poll_list = []

    # główna pętla
    while float(pos)>0 :
        # czyszczenie ekranu w zależności od systemu operacyjnego
        if os.name == "posix":
                os.system('clear')
        elif os.name in ("nt", "dos", "ce"):
                os.system('CLS')


        # wyświetanie menu
        i = 1
        for st in st_m:
            if len(st)==1:
                for n,v,s in st:
                    txt =""
                    for t in v.decode('utf-8').split("%%%"):
                        txt+= t + " "
                    print ("  " + str(i)+ '.0 ' + txt).encode('utf-8')
                    good_res.append(str(i)+'.0')
                    i+=1
                print "------".encode('utf-8')
            else:
                n1, v1, s1 = st[0]
                print (str(i)+'.0'+ " " +v1.decode('utf-8').split("%%%").pop(0) + u' ( powiązane )').encode('utf-8')
                good_res.append(str(i)+'.0')
                j=1
                for n,v,s in st:
                    
                    vl = v.decode('utf-8').split("%%%")
                    vl.pop(0)
                    txt =""
                    for t in vl:
                        txt+= t + " "
                    print ("  " + str(i)+'.'+str(j)+ " " + txt).encode('utf-8')
                    good_res.append(str(i)+'.'+str(j))
                    j+=1
                i+=1
                print "------".encode('utf-8')
                
        print u"ankiety do wysłania:".encode('utf-8')
        choosen_list = u"["
        for p in poll_list:
            choosen_list += unicode(p)+u","
        choosen_list += u"]"
        print choosen_list.encode('utf-8')
        print u"podaj numer ankiety do wysłania".encode('utf-8')
        print u"u 'nr_ankiety' usuwa numer ankiety z listy".encode('utf-8')
        print u"(  0 - wysyła dane, -1 - konczy działanie )".encode('utf-8')

        # pobieranie polecenia użytkownika
        pos=raw_input()
        try:
            if (len(pos.split(" "))==2) and (pos.split(" ")[0]=='u'):
                pos=pos.split(" ")[1]
                poll_list.remove(pos)
            elif (pos in good_res) and not(pos in poll_list):
                poll_list.append(pos)
        except ValueError, err:
            pos='50.0'
            
        try:
            float(pos)
        except ValueError, err:
            pos='50.0'
        poll_list.sort()
    poll_list.sort()
    return poll_list

def to_list(st):
        
    """

    Convert response to list.
        
    """

    # sprowadzamy odpowiedz serwera do listy
    # korzystamy z tego ze elementy listy są oddzielone separatorami: ??? &&& ***
    
    result =[]
    st_l = st.split("???")
    for blocks in st_l:
            blocks_l = blocks.split("&&&")
            if len(blocks_l)<2:
                block = blocks_l[0].split("***")
                if block[0] != "":
                    nr = block.pop(0)
                    view = block.pop(0)
                    key = block.pop(0)
                    result.append([(nr,view,RSA.importKey(key))])
            else:
                block_result = []
                for block in blocks_l:
                    b = block.split("***")
                    if b[0] != "":
                        nr = b.pop(0)
                        view = b.pop(0)
                        key = b.pop(0)
                        block_result.append((nr,view,RSA.importKey(key)))
                if block_result!=[]:
                    result.append(block_result)
    return  result
        
def client():
    """

    Main client function.
        
    """

    # pobieramy użytkownika
    idUser,passwordUser = get_user()
    # przesyłamy dane użytkownika i otrzymujemy listę ankiet
    pollSt = get_poll_list(idUser, passwordUser)

    # sprawdzenie czy w trakcie pobierania kluczy do ankiet nie powstał błąd
    if len(pollSt.split('???'))<2:
        print u"nie udało się pobrać biletu".encode('utf-8')
        print pollSt.decode("utf-8").encode('utf-8')
        return

    # zamiana odpowiedzi servera na postać listową
    pollList = to_list(pollSt)

    # menu do wybierania ankiet
    sendList = menu(pollList)

    # -1 kończy działanie bez wysyłania zapytania
    if sendList.pop(0) == '-1':
        print u"Pobieranie biletów zostało anulowane".encode('utf-8')
        return

    # wybieranie odpowiednich kluczy publicznych
    keys = get_key(pollList,sendList)

    # przesyłanie kolejnych zestawów kluczy
    # nr - numer ankiety
    # m - klucz do kodowania
    # key - klucz publiczny ankiety
    for nr,m,key in keys:
        send_package( idUser, passwordUser, nr ,key.e, key.n, m)

if __name__ == "__main__":
    client()
