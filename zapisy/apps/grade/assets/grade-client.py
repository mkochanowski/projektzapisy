#!/usr/bin/env python

"""Przykładowy klient tworzący karty do oceny

    Moduł zawiera przykładową implementację
    generowania kluczy do oceny zajęć w klasie Tickets
    oraz funkcje pomocnicze.
    Uruchomienie pliku rozpoczyna proces tworzenia kart.
"""
from typing import Union, Iterable, Type, Mapping, Dict, NoReturn
from io import TextIOBase
from getpass import getpass
from sys import stdout, stderr, argv
from math import gcd
from random import getrandbits
from hashlib import sha256
import requests

Poll = Dict[str, Union[int, Mapping[str, Union[str, int]]]]


def rand(bits: int) -> int:
    """Zwraca losową liczbę.

    Zwraca bits-bitową losową liczbę całkowitą (bits>=1)
    najbardziej znaczący bit jest ustawiony.
    """

    return getrandbits(bits) | 1 << (bits - 1)


def modinv(a: int, n: int) -> int:
    """Odwrotność modulo.

    Zwraca t,
    a*t = 1 mod n.
    Alogrytm Euklidesa.
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


def convert_key(key: Mapping[str, str]) -> Dict[str, int]:
    """Zmienia wartości klucza na liczby."""

    return {
        'n': int(key['n']),
        'e': int(key['e'])
    }


def try_again() -> bool:
    """Pyta użytkownika czy próbować ponownie."""

    res = input("Próbować jeszcze raz? [T/n]:")
    if not res or res[0] == 't' or res[0] == 'T':
        return True
    else:
        return False


class Tickets:
    """Główna logika generowania kluczy do oceny zajęć."""

    url: str = 'https://zapisy.ii.uni.wroc.pl/'
    # Szablon do wypisania kluczy.
    template: str = ("[{title}] {name} \nid: {id} \n{ticket} \n{signed_ticket} \n" +
                     ('-' * 34) + " \n")

    def __init__(self, out_file: Type[TextIOBase], backup_file: Type[TextIOBase]) -> None:
        """Tworzy obiekt tworzący karty do głosowania.

        Aby uzyskać karty należy użyć metody run.

        Args:
            out_file: do tego będą zapisane klucze w finalnym formacie.
            backup_file: do tego będą zapisane dane diagnostyczne
                i surowe dane podpisanych kart.
        """

        # Połączenie z serwerem jest obsługiwane przez bibiliotekę requests.
        self.client: Type[requests.sessions.Session] = requests.session()
        self.poll_data: Iterable[Mapping[str, Union[Poll, Mapping[str, int]]]]
        self.data: Dict[int, Poll] = dict()
        self.signed_blind_tickets: Iterable[Mapping[str, Union[int, str]]]
        self.out_file = out_file
        self.backup_file = backup_file

    def run(self) -> None:
        """Uruchamia tworzenie kart.

        Uruchamia metody w odpowiedniej kolejności
        oraz informuje użytkownika o aktualnym stanie.
        """

        # Logowanie jest wymagane do pobrania kluczy publicznych
        # oraz do podpisania kluczy do oceny.
        while not self.login():
            print("Nie Zalogowano")
        print("Zalogowano")

        while not self.get_public_keys():
            print("Nie udało się pobrać kluczy")
            if not try_again():
                return
        print("Udało się pobrać klucze")

        print("Generowanie kart")
        self.prepare_tickets()
        print("Karty wygenerowane")

        while not self.get_signed_tickets():
            print("Nie udało się uzyskać podpisanych kart")
            print("Podpisać karty można tylko raz, możliwe że już to zrobił(aś/eś)")
            if not try_again():
                return
        print("Udało się uzyskać podpisane karty")

        print("Odślepianie podpisanych kart")
        self.unblind_tickets()
        print("Podpisane karty odślepione")

        print("Zapis kart")
        self.save()
        print("Gotowe")

    def login(self) -> bool:
        """Logowanie"""

        # Weź pierwszy CSRF token.
        self.client.get(self.url)

        # Wyślij dane do logowania z tokenem CSRF.
        data = {
            'username': self.username,
            'password': self.password,
            'csrfmiddlewaretoken': self.csrftoken
        }

        response = self.client.post(self.url + 'users/login/', data=data)
        # Proste sprawdzenie czy logowanie się powiodło.
        return response.ok and response.text.find(
            '/users/password-change/') != -1

    def get_public_keys(self) -> bool:
        """Pobranie kluczy publicznych ankiet."""

        # Należy wysłać token CSRF.
        data = {
            'csrfmiddlewaretoken': self.csrftoken
        }

        response = self.client.post(
            self.url + 'grade/ticket/ajax_get_keys', data=data)

        if response.ok:
            # Zwrócone dane to lista obiektów
            # [{'key': {'n': string, 'e': string }, 'pool_info': X }]
            # X jest obiektem z conajmniej polem 'title' oraz 'id'
            # może mieć również pola 'type', 'course_name', 'teacher_name'
            # jeśli ich nie ma jest to ankieta ogólna.
            self.poll_data = response.json()
            return True
        return False

    @staticmethod
    def generate_ticket(n: int) -> Dict[str, int]:
        """Tworzy kartę i kopertę."""

        bits = n.bit_length()

        randomize = True
        while randomize:
            m = rand(bits)
            k = rand(bits)
            randomize = k > n or m > n or gcd(k, n) != 1
        return {'k': k, 'm': m}

    @staticmethod
    def blind_ticket(ticket: Mapping[str, int], public_key: Mapping[str, int]) -> int:
        """Zaślepia pojedynczy klucz/ wsadza kartę do koperty."""

        m_sha256 = int(sha256(str(ticket['m']).encode('ascii')).hexdigest(), 16)
        k_pow_e = pow(ticket['k'], public_key['e'], public_key['n'])
        t = (m_sha256 * k_pow_e) % public_key['n']
        return t

    def prepare_tickets(self) -> None:
        """Generowanie kluczy/kart i zaślepianie/wsadzanie do kopert do podpisania."""

        for data in self.poll_data:
            poll = {
                'public_key': convert_key(data['key']),
                'poll_info': data['poll_info']
            }

            ticket = Tickets.generate_ticket(poll['public_key']['n'])

            poll['m'] = ticket['m']
            poll['k'] = ticket['k']
            poll['t'] = Tickets.blind_ticket(ticket, poll['public_key'])
            self.data[data['poll_info']['id']] = poll

        del self.poll_data

    def get_signed_tickets(self) -> bool:
        """Wyślij karty w kopertach do podpisania."""

        data = [{
            'id': id,
            'ticket': str(poll['t']),
        } for id, poll in self.data.items()]

        headers = {
            'X-Csrftoken': self.csrftoken,
        }

        response = self.client.post(
            self.url + 'grade/ticket/ajax_sign_tickets', json=data, headers=headers)

        if response.ok:
            # Zwrócone dane to lista obiektów
            # [{
            #    'status': 'OK'|'ERROR',
            #    'id': int,
            #    'message'|'signature': string,
            # }]
            # wartość 'message' to informacja o błędzie
            # obecna gdy status to 'ERROR',
            # wartość 'signature' to podpisana karta w kopercie
            # obecna gdy status to 'OK'.
            self.signed_blind_tickets = response.json()
            # Karty można podpisać tylko raz
            # dlatego nie przetworzoną odpowiedź należy zapisać,
            # aby móc wznowić w razie problemów.
            self.backup_file.write(response.text)
            return True
        return False

    def unblind_tickets(self) -> None:
        """Wyjęcie podpisanych kart z kopert."""

        for data in self.signed_blind_tickets:
            id = data['id']
            if data['status'] == 'OK':
                st = int(data['signature'])
                public_key = self.data[id]['public_key']
                rk = modinv(self.data[id]['k'], public_key['n'])
                self.data[id]['s'] = (st * rk) % public_key['n']
            else:
                self.backup_file.write("Błąd id: {id} \t| {message}\n".format(**data))
                del self.data[id]

        del self.signed_blind_tickets

    def save(self) -> None:
        """Zapisanie kopert w ustalonym formacie."""

        for id, poll in self.data.items():
            data = {
                'title': poll['poll_info']['title'],
                'name': 'Ankieta ogólna ' if not poll['poll_info'].get('course_name', False) else
                        '{course_name} \n{type}: {teacher_name}'.format(
                            **poll['poll_info']),
                'id': id,
                'ticket': str(poll['m']),
                'signed_ticket': poll['s'],
            }
            self.out_file.write(self.template.format(**data))

    @property
    def csrftoken(self) -> Union[str, NoReturn]:
        """get CSRF Token"""
        if 'csrftoken' in self.client.cookies:
            return self.client.cookies['csrftoken']
        raise Exception("Brak tokenu CSRF")

    @property
    def username(self) -> str:
        """get username"""
        return input('Login: ')

    @property
    def password(self) -> str:
        """get password"""
        return getpass('Password: ')


USAGE = """
Użycie: {} [opcje] [plik_z_kartami [plik_backup]]
plik_z_kartami domyślnie to standardowe wyjście
plik_backup domyślnie to standardowe wyjście błędów

Opcje:
  -h, --help \tWyświetla ten tekst i kończy działanie.
"""
if __name__ == "__main__":
    if '-h' in argv or '--help' in argv:
        print(USAGE.format(argv[0]))
    else:
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
