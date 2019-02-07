#!/bin/python

"""
   Przykład generowania i walidowania
   kluczy do oceny zadań
"""
from getpass import getpass
from sys import stdout, stderr, argv
from math import log, gcd
from random import getrandbits
from hashlib import sha256
import json
import requests


def rand(bits):
    """
       return bits-bitową losową liczbę całkowitą (bits>=1)
       najbardziej znaczący bit jest ustawiony
    """
    return getrandbits(bits) | 1 << (bits - 1)


def modinv(a, n):
    """
       return t
       a*t = 1 mod n
       alogrytm Euklidesa
    """
    t, nt = 0, 1
    r, nr = n, a
    while nr != 0:
        q = r // nr
        t, nt = nt, t - q * nt
        r, nr = nr, r - q * nr
    if r > 1:
        return None
    if t < 0:
        return t + n
    return t


class Tickets:
    """
       Główna logika generowania kluczy do głosowania
    """
    url = 'https://zapisy.ii.uni.wroc.pl/'
    template = "[{title}] {name} \nid: {id} \n{ticket} \n{signed_ticket} \n" + \
        ('-' * 34) + " \n"

    def __init__(self, out_file, backup_file):
        # połączenie z serwerem jest obsługiwane przez bibiliotekę requests
        self.client = requests.session()
        self.loggedin = False
        self.poll_data = None
        self.public_keys = []
        self.poll_info = []
        self.ks = []
        self.ms = []
        self.ts = []
        self.signed_blind_tickets = None
        self.signed_tickets = []
        self.out_file = out_file
        self.backup_file = backup_file

    def run(self):
        """
           Uruchamia główną logikę
        """

        # logowanie jest wymagane do pobrania kluczy publicznych
        # oraz do podpisania kluczy do głosowania
        while not self.loggedin:
            self.login()
            if self.loggedin:
                print("Zalogowano")
            else:
                print("Nie Zalogowano")

        while self.poll_data is None:
            self.get_public_keys()
            if self.poll_data is None:
                print("Nie udało się pobrać kluczy")
                input()
            else:
                print("Udało się pobrać klucze")

        print("Generowanie kart")
        self.generate_tickets()
        print("Karty wygenerowane")

        while self.signed_blind_tickets is None:
            self.get_signed_tickets()
            if self.signed_blind_tickets is None:
                print("Nie udało się uzyskać podpisanych kart")
                print("Podpisać karty można tylko raz, możliwe że już to zrobił(aś/eś)")
                input()
            else:
                print("Udało się uzyskać podpisane karty")

        print("Odślepianie podpisanych kart")
        self.unblind_tickets()
        print("Podpisane karty odślepione")

        print("Zapis kart")
        self.save()
        print("Gotowe")

    def login(self):
        """
           Logowanie
        """
        # weź pierwszy CSRF token
        self.client.get(self.url)

        # wyślij dane do logowania z tokenem CSRF
        data = {
            'username': self.username,
            'password': self.password,
            'csrfmiddlewaretoken': self.csrftoken
        }

        response = self.client.post(self.url + 'users/login/', data=data)
        # proste sprawdzenie czy logowanie się powiodło
        self.loggedin = response.ok and response.text.find(
            '/users/password-change/') != -1

    def get_public_keys(self):
        """
           Pobranie kluczy publicznych ankiet
        """
        # należy wysłać token CSRF
        data = {
            'csrfmiddlewaretoken': self.csrftoken
        }
        # oraz wysłać jako AJAX
        headers = {
            'X-Requested-With': 'XMLHttpRequest'
        }

        response = self.client.post(
            self.url + 'grade/ticket/ajax_get_keys', data=data, headers=headers)

        if response.ok:
            # zwrócone dane to lista obiektów
            # [{'key': {'n': string, 'e': string }, 'pool_info': X }]
            # X jest oiektem z conajmniej polem 'title' oraz 'id'
            # może mieć również pola 'type', 'course_name', 'teacher_name'
            # jeśli ich nie ma jest to ankieta ogólna
            self.poll_data = response.json()

    def generate_tickets(self):
        """
           Generowanie kluczy/kart i zaślepianie/wsadzanie do kopert do podpisania
        """
        for data in self.poll_data:
            n = int(data['key']['n'])
            e = int(data['key']['e'])

            self.public_keys.append({'n': n, 'e': e})
            self.poll_info.append(data['poll_info'])

            bits = 1 if n == 0 else int(log(n, 2)) + 1

            condition = True
            while condition:
                m = rand(bits)
                k = rand(bits)
                condition = k > n or m > n or gcd(k, n) != 1

            self.ks.append(k)
            self.ms.append(m)
            m_sha256 = int(sha256(str(m).encode('ascii')).hexdigest(), 16)
            k_pow_e = pow(k, e, n)
            t = (m_sha256 * k_pow_e) % n

            self.ts.append(t)

        self.poll_data = None

    def get_signed_tickets(self):
        """
           Wyślij karty w kopertach do podpisania
        """
        data = [{
            'id': poll_info['id'],
            'ticket': str(ticket),
        } for (poll_info, ticket) in zip(self.poll_info, self.ts)]

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'X-Csrftoken': self.csrftoken,
        }

        response = self.client.post(
            self.url + 'grade/ticket/ajax_sign_tickets', json=data, headers=headers)

        if response.ok:
            # zwrócone dane to lista obiektów
            # [{'signature': string }]
            # wartość 'signature' to informacja o błędzie
            # lub podpisana karta w kopercie
            self.signed_blind_tickets = response.json()
            # karty można podpisać tylko raz
            # dlatego nie przetworzoną odpowiedź należy zapisać
            # aby móc wznowić w razie problemów
            self.backup_file.write(response.text)

    def unblind_tickets(self):
        """
           Wyjęcie podpisanych kart z kopert
        """
        error_msgs = [
            'Nie jesteś przypisany do tej ankiety',
            'Bilet już pobrano',
        ]
        for index, data in enumerate(self.signed_blind_tickets):
            if data['signature'] in error_msgs:
                self.signed_tickets.append(data['signature'])
            else:
                st = int(data['signature'])
                public_key = self.public_keys[index]
                rk = modinv(self.ks[index], public_key['n'])
                self.signed_tickets.append((st * rk) % public_key['n'])

        self.signed_blind_tickets = None

    def save(self):
        """
           Zapisanie kopert w ustalonym formacie
        """
        for poll_info, ticket, signed_ticket in zip(self.poll_info, self.ms, self.signed_tickets):
            data = {
                'title': poll_info['title'],
                'name': 'Ankieta ogólna ' if not poll_info.get('course_name', False) else
                        '{course_name} \n{type}: {teacher_name}'.format(
                            **poll_info),
                'id': poll_info['id'],
                'ticket': str(ticket),
                'signed_ticket': signed_ticket
            }
            self.out_file.write(self.template.format(**data))

    @property
    def csrftoken(self):
        """
           get CSRF Token
        """
        if 'csrftoken' in self.client.cookies:
            return self.client.cookies['csrftoken']
        raise Exception("Brak tokenu CSRF")

    @property
    def username(self):
        """
           get username
        """
        return input('Login: ')

    @property
    def password(self):
        """
           get password
        """
        return getpass('Password: ')


# użycie: ./grade-client.py [plik_z_kartami [plik_backup]]
# plik_z_kartami domyślnie to standardowe wyjście
# plik_backup domyślnie to standardowe wyjście błędów
if __name__ == "__main__":
    FILE = stdout
    BACKUP = stderr
    if len(argv) > 1:
        FILE = open(argv[1], 'w')
    if len(argv) > 2:
        BACKUP = open(argv[2], 'w')

    Tickets(FILE, BACKUP).run()

    if FILE != stdout:
        FILE.close()
    if BACKUP != stderr:
        BACKUP.close()
