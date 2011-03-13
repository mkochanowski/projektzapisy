0. System Fereol Mobile.
    - Fereol Mobile jest lekką, okrojoną wersją systemu zapisów Fereol.
    - System umożliwia:
        - zapisywanie na przedmiot, 
        - wypisywanie z przedmiotu, 
        - przeglądanie swojego planu zajęć,
        - przeglądanie planów zajęć innych studentów,
        - przeglądanie listy przedmiotów prowadzonych w danym semestrze, z podziałem na:
            - listę przedmiotów, na które jest się zapisanym,
            - listę przedmiotów, na które się głosowało,
            - listę przedmiotów przypiętych,
            - listę wszystkich przedmiotów.
    - Aplikacja korzysta z bazy danych głównego systemu.
    - Aplikacja automatycznie wykrywa wejście z urządzenia mobilnego i dokonuje przekierowania na wersję mobliną systemu.

1. Uruchamianie i konfiguracja projektu.
    - Należy w pliku 'settings.py' dodać wpis (istotna jest kropka na początku): 
        SESSION_COOKIE_DOMAIN = ".nazwa.domeny" .
      Jest on potrzebny, aby współdzielić sesję między subdomenami. 
      Django domyślnie ustawia ciasteczka tylko dla domeny głównej.

    - Należy udostępnić na serwerze subdomenę "m.".

2. Konfiguracja lokalna.

    - Po dodaniu ww. wpisu pojawia się problem z ustawianiem ciasteczek dla domeny bez kropki (localhost). 
      Aby odpalić projekt lokalnie, można więc w '/etc/hosts' przypisać do 127.0.0.1 
      np. localhost.localhost i m.localhost.localhost (oraz w settings.py: SESSION_COOKIE_DOMAIN = ".localhost.localhost").


3. Moduły.
	Opisy modułów umieszczone są w poszczególnych plikach projektu.
