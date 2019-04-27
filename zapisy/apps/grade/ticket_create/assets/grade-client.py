#!/usr/bin/env python
import os
import argparse
import json
from math import gcd
from secrets import randbelow
from typing import Dict
from getpass import getpass
from urllib.parse import urljoin
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Util.number import inverse
import requests

URL = os.getenv('URL', 'https://zapisy.ii.uni.wroc.pl/')


def hash_(m: int) -> int:
    """We are using hash function to disable multiplicative properties
    of RSA encryption/decryption. In other words, if E(m) is standard rsa
    encryption/decryption, then E(m*k) = E(m) * E(k), but if we set
    E'(m) = E(H(m)), where H is hash function, then E'(m*k) != E'(m) * E'(k).
    If we didn't use that, you would be able to generate many tickets, just
    by knowing factors of m.
    """
    h = SHA256.new()
    h.update(str(m).encode())
    return int(h.hexdigest(), 16)


def blind(pub_key, m, r):
    return (m * pow(r, pub_key.e, pub_key.n)) % pub_key.n


def unblind(pub_key, m, r):
    return (m * inverse(r, pub_key.n)) % pub_key.n


class Ticket:
    """Class which is responsible for generating and holding ticket data."""
    def __init__(self, pub_key):
        # This while loop could be omitted, since condition GCD(r, pub_key.n) != 1 will probably
        # never happen in our universe lifetime, but lets do that for the sake of correctness.
        while True:
            m = randbelow(pub_key.n)
            r = randbelow(pub_key.n)
            if gcd(r, pub_key.n) == 1:
                break
        self.m = m
        self.r = r


class PollData:
    """This class serves the purpose of holding data related to poll"""
    def __init__(self, poll: Dict, ticket=None):
        self.pub_key = RSA.construct((int(poll['key']['n']), int(poll['key']['e'])))
        self.name = poll['poll_info']['name']
        self.type = poll['poll_info']['type']
        self.id = poll['poll_info']['id']
        self.ticket = ticket

    def serialize_blinded_ticket(self) -> Dict:
        assert self.ticket is not None
        ticket_to_sign = blind(self.pub_key, hash_(self.ticket.m), self.ticket.r)
        return {
            'ticket': str(ticket_to_sign),
            'id': self.id,
        }


class TicketCreate:
    """Main logic."""
    def __init__(self, url):
        self.url = url
        self.client = requests.Session()

    def _post(self, path: str, *args, **kwargs) -> requests.Response:
        """Wrapper for self.client.post."""
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['X-CSRFToken'] = self.csrf_token
        response = self.client.post(urljoin(self.url, path), *args, **kwargs)
        response.raise_for_status()
        return response

    def login(self) -> None:
        self.client.get(self.url)
        username = input('Username: ')
        password = getpass('Password: ')
        data = {
            'username': username,
            'password': password,
        }

        response = self._post('/users/login/', data=data)
        assert response.ok
        login_success_check = self._post('/grade/ticket/tickets-generate', allow_redirects=False)
        if login_success_check.status_code != 200:
            raise RuntimeError("Login failed")

    def get_polls(self) -> Dict[int, PollData]:
        """First step of the protocol, query the server for polls metadata(name, type, id)
        and public keys.

        Returns:
            Dict with id as a key, and as a value, data received from the server,
            wrapped in PollData class.
        """
        res = self._post('/grade/ticket/get-poll-data')
        polls = res.json()
        return {
            poll['poll_info']['id']: PollData(poll)
            for poll in polls['poll_data']
        }

    def get_signed_tickets(self, polls: Dict[int, PollData]):
        """Second step of the protocol, after generating tickets, sends them,
        blinded, to the server for signing.
        """
        data = {
            'signing_requests': []
        }

        for poll_data in polls.values():
            ticket = Ticket(poll_data.pub_key)
            poll_data.ticket = ticket
            signing_request = poll_data.serialize_blinded_ticket()
            data['signing_requests'].append(signing_request)
        return data

    def get_tickets(self):
        """Main function."""
        self.login()
        polls = self.get_polls()
        signing_request = self.get_signed_tickets(polls)
        res = self._post('/grade/ticket/sign-tickets', json=signing_request).json()
        tickets_for_user = {
            'tickets': []
        }
        for signed_ticket in res:
            if signed_ticket['status'] == 'ERROR':
                print('ERROR: {}'.format(signed_ticket['message']))
                continue
            poll_data = polls[signed_ticket['id']]
            unblinded_signature = unblind(poll_data.pub_key, int(signed_ticket['signature']), poll_data.ticket.r)
            tickets_for_user['tickets'].append({
                'name': poll_data.name,
                'type': poll_data.type,
                'id': poll_data.id,
                'ticket': str(poll_data.ticket.m),
                'signature': str(unblinded_signature),
            })
        return tickets_for_user

    @property
    def csrf_token(self):
        """get CSRF Token"""
        if 'csrftoken' in self.client.cookies:
            return self.client.cookies['csrftoken']
        raise AttributeError("CSRF token not found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('f', type=str, help='Path to the output file.')
    args = parser.parse_args()

    tickets_creator = TicketCreate(URL)
    tickets = tickets_creator.get_tickets()

    with open(args.f, 'w') as f:
        f.write(json.dumps(tickets, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
