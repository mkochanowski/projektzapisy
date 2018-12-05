## Setup
### Środowisko developerskie
Na ten moment zrobione jest jedynie środowisko developerskie, składa się ono z 3 kontenerów:

1. backend(app) - Korzysta z obrazu pythona, sam w sobie nie ma żadnego stanu(może oprócz pakietów pythonowych, ale w środowisku produkcyjnym będą one zawarte w obrazie dockera), służy do tego by odpalić server korzystając z django.
2. frontend - Kontener służący do kompilowania assetów do plików statycznych. Na ten moment jest to zwykły obraz nodejs, ale w przyszłości może się to zmienić.
3. postgresql - Baza danych oparta na gotowym obrazie postgresa. Stan bazy(użytkownicy, dane itp.) jest trzymany w volume `postgresql-data`.

Katalog `zapisy/` jest współdzielony między hostem i kontenerem, więc zmiany w kodzie powinny automatycznie przeładowywać server, w katalogu `zapisy/pipcache` są cachowane pakiety ściągane przez pipa, dzięki czemu trzeba długo czekać tylko przy pierwszym uruchomieniu.

## Korzystanie z `run.py`

`run.py` to nakładka na wykonywanie poleceń dockerowych. Aby go używać należy ściągnąć pakiet `click`(`pip3 install click`). Wszystkie komendy powinny być udokumentowane jako docstring który można wyświetlić poleceniem `./run.py COMMAND --help`. Przykładowo:

- By uruchomić server wydajemy polecenie `./run.py server`.
- By przekompilować wszystkie pliki statyczne(bez potrzeby restartowania servera) wydajemy polecenie `./run.py static compile`.
- By załadować dump bazy wydajemy polecenie `./run.py PATH`, gdzie `PATH` to ścieżka relatywna do katalogu `db_backups`(dump musi być w tym katalogu).

Znajduje się tam więcej poleceń, ale nie powinny być problemów z doczytaniem do czego służą używając `--help`.

## Jak rozpocząć pracę z dockerem

1. Zainstalować dockera.
2. W głowym katalogu(czyli tym w którym znajduje się `docker-compose.yml`) wpisać polecenie `docker-compose up -d`. Jeśli wszystko działa to wykonując polecenie `docker-compose ps` powinniśmy widzieć wszystkie kontenery w stanie `Up`. Uruchamiając dockera po raz pierwszy trzeba chwilę poczekać aż zostaną ściągnięte wszystkie pakiety do pythona, można sprawdzić na jakim etapie jest pobieranie poleceniem `docker-compose logs -f app`.
3. Do katalogu db_backups wrzucamy dump bazy danych(np. `dump.sql`) a potem wykonujemy polecenie `./run.py db load dump.sql`(tego kroku nie trzeba wykonywać za każdym uruchomieniem dockera, wystarczy raz).
4. Możemy teraz odpalić server poleceniem `./run.py server`.
5. Aby "wyłączyć" wszystkie kontereny wykonujemy polecenie `docker-compose down`.

## Problemy
### Dostęp do plików
Ten problem występuje prawdopodobnie tylko na linuxach(nie testowane na innych systemach). Polega on na tym że użytkownikiem w środku kontenera jest root(czyli użytkownik z UID 0), więc tworząc pliki we współdzielonych katalogach, ich właścicielem będzie root, przez co prawdopodobnie nie będziemy mieli do nich dostępu(bez `sudo` lub logowania na roota) z poziomu hosta.

Aby rozwiązać ten problem należy zmapować naszego użytkownika na dockerowego roota.
W pliku `/etc/docker/daemon.json`(jeśli nie istnieje to go tworzymy) wpisujemy:

```json
{
  "userns-remap": "$USER"
}
```

Następnie do pliku `/etc/subuid` dopisujemy linijkę:
```
$USER:$USERID:1
```

gdzie `$USER` to nazwa naszego użytkownika, a $USERID to jego uid(uid można sprawdzić poleceniem `id -u`). Zazwyczaj użytkownicy mają uid 1000.
