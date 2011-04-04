# -*- coding: utf8 -*-
# Author: Pawel Kacprzak

from random import randint as rand
from random import choice

# STATIC SUBJECTS DATA; DO NOT CHANGE IT UNLESS CHANGING clean_data.json  / DEPENCENCY /
SUBJECTS = [{"lectures": 30, "name": "Wdra\u017canie system\u00f3w klasy ERP", "entity": 100, "semester": 1, "exercises": 30, "laboratories": 0, "type": 5, "slug": "wdrazanie-systemow-klasy-erp", "description": "Opis"}, {"lectures": 30, "name": "Text mining", "entity": 101, "semester": 1, "exercises": 30, "laboratories": 0, "type": 5, "slug": "text-mining", "description": "Opis"}, { "lectures": 30, "name": "Algorytmy tekstowe", "entity": 102, "semester": 1, "exercises": 30, "laboratories": 0, "type": 5, "slug": "algorytmy-tekstowe", "description": "Opis"}, {"lectures": 30, "name": "Zastosowania wielomian\u00f3w Czebyszewa", "entity": 103, "semester": 2, "exercises": 30, "laboratories": 0, "type": 5, "slug": "zastosowania-wielomianow-czebyszewa", "description": "Opis"}, {"lectures": 30, "name": "Wprowadzenie do logiki formalnej", "entity": 104, "semester": 2, "exercises": 30, "laboratories": 0, "type": 5, "slug": "wprowadzenie-do-logiki-formalnej", "description": "Opis"}, {"lectures": 30, "name": "Teoretyczne podstawy j\u0119zyk\u00f3w programowania",  "entity": 105, "semester": 2, "exercises": 30, "laboratories": 0, "type": 5, "slug": "teoretyczne-podstawy-jezykow-programowania", "description": "Opis"}, {"lectures": 30, "name": "Seminarium: Protoko\u0142y Rynku Elektronicznego", "entity": 106, "semester": 2, "exercises": 0, "laboratories": 0, "type": 6, "slug": "seminarium-protokoly-rynku-elektronicznego", "description": "Opis"}, {"lectures": 30, "name": "Procesory graficzne w obliczeniach r\u00f3wnoleg\u0142ych (CUDA)", "entity": 107, "semester": 1, "exercises": 0, "laboratories": 30, "type": 6, "slug": "procesory-graficzne-w-obliczeniach-rownoleglych-cuda", "description": "Opis"}, {"lectures": 30, "name": "Kurs j\u0119zyka Lua", "entity": 108, "semester": 1, "exercises": 0, "laboratories": 15, "type": 6, "slug": "kurs-jezyka-lua", "description": "Opis"}, {"lectures": 30, "name": "Seminarium: Krzywe i powierzchnie w grafice komputerowej", "entity": 109, "semester": 2,"exercises": 0, "laboratories": 0, "type": 7, "slug": "seminarium-krzywe-i-powierzchnie-w-grafice-komputerowej", "description": "Opis"}, {"lectures": 30, "name": "Seminarium: Algorytmika: nowe osi\u0105gni\u0119cia i trendy", "entity": 110, "semester": 2, "exercises": 0, "laboratories": 0,"type": 7, "slug": "seminarium-algorytmika-nowe-osiagniecia-i-trendy", "description": "Opis"}, {"lectures": 30, "name": "Kurs j\u0119zyka ANSI C z elementami C++", "entity": 111, "semester": 1, "exercises": 0, "laboratories": 30, "type": 6, "slug": "kurs-jezyka-ansi-c-z-elementami-c", "description": "Opis"}, {"lectures": 30, "name": "Rachunek lambda", "entity": 112, "semester": 2, "exercises": 30, "laboratories": 0, "type": 5, "slug": "rachunek-lambda", "description": "Opis"}, {"lectures": 30, "name": "Logika dla informatyk\u00f3w", "entity": 113, "semester": 1, "exercises": 30, "laboratories": 0, "type": 1, "slug": "logika-dla-informatykow", "description": "Opis"}, {"lectures": 30, "name": "Programowanie funkcyjne", "entity": 114, "semester": 2, "exercises": 30, "laboratories": 0, "type": 5, "slug": "programowanie-funkcyjne", "description": "Opis"}, {"lectures": 30, "name": "Bazy danych 2", "entity": 115, "semester": 1, "exercises": 15, "laboratories": 15, "type": 5, "slug": "bazy-danych-2", "description": "Opis"}, {"lectures": 30, "name": "Analiza numeryczna (M)", "entity": 116, "semester": 1, "exercises": 30, "laboratories": 15, "type": 2, "slug": "analiza-numeryczna-m", "description": "Opis"}, {"lectures": 30, "name": "Programowanie", "entity": 117, "semester": 2, "exercises": 30, "laboratories": 15, "type": 2, "slug": "programowanie", "description": "Opis"}, {"lectures": 30, "name": "Modelowanie zjawisk przyrodniczych", "entity": 118, "semester": 2, "exercises": 0, "laboratories": 30, "type": 5, "slug": "modelowanie-zjawisk-przyrodniczych", "description": "Opis"}, {"lectures": 0, "name": "Licencjacki projekt programistyczny", "entity": 119, "semester": 2, "exercises": 0, "laboratories": 30, "type": 6, "slug": "licencjacki-projekt-programistyczny", "description": "Opis"}, {"lectures": 30, "name": "Analiza matematyczna", "entity": 120, "semester": 1, "exercises": 45, "laboratories": 0, "type": 1, "slug": "analiza-matematyczna", "description": "Opis"}, {"lectures": 30, "name": "Sieci neuronowe", "entity": 121, "semester": 1, "exercises": 0, "laboratories": 30, "type": 5, "slug": "sieci-neuronowe", "description": "Opis"}, {"lectures": 30, "name": "Kurs: UNIX - \u015brodowisko i narz\u0119dzia programowania", "entity": 122, "semester": 2, "exercises": 0, "laboratories": 30, "type": 6, "slug": "kurs-unix-srodowisko-i-narzedzia-programowania", "description": "Opis"}, {"lectures": 30, "name": "Seminarium: Zastosowania algorytm\u00f3w ewolucyjnych", "entity": 123, "semester": 1, "exercises": 0, "laboratories": 0, "type": 7, "slug": "seminarium-zastosowania-algorytmow-ewolucyjnych", "description": "Opis"}, {"lectures": 30, "name": "Kurs programowania pod Windows w technologii .NET", "entity": 124, "semester": 2, "exercises": 0, "laboratories": 30, "type": 6, "slug": "kurs-programowania-pod-windows-w-technologii-net", "description": "Opis"}, {"lectures": 30, "name": "J\u0119zyki formalne i z\u0142o\u017cono\u015b\u0107 obliczeniowa", "entity": 125, "semester": 2, "exercises": 30, "laboratories": 0, "type": 3, "slug": "jezyki-formalne-i-zlozonosc-obliczeniowa", "description": "Opis"}, {"lectures": 30, "name": "Bazy danych", "entity": 126, "semester": 2, "exercises": 15, "laboratories": 15, "type": 4, "slug": "bazy-danych", "description": "Celem wyk\u0142adu jest om\u00f3wienie zasad konstrukcji relacyjnych baz danych oraz opanowanie przez s\u0142uchaczy umiej\u0119tno\u015bci profesjonalnej obs\u0142ugi systemu baz danych od strony u\u017cytkownika, czyli:\r\n\r\n* umiej\u0119tno\u015bci zaprojektowania i zdefiniowania relacyjnej bazy danych dla rzeczywistego zagadnienia;\r\n\r\n* sprawnego wyszukiwania i odzyskiwania informacji z baz danych przypomocy j\u0119zyka SQL;\r\n\r\n* pisania aplikacji z dost\u0119pem do bazy danych;\r\n\r\n* efektywnego wykorzystania dodatkowych mo\u017cliwo\u015bci systemu (perspektyw, transakcji, wi\u0119z\u00f3w, itp.).\r\n\r\nPonadto wyk\u0142ad pozwala s\u0142uchaczom pozna\u0107 elementy system\u00f3w baz danych spoza warstwy u\u017cytkownika (system zarz\u0105dzania transakcjami, zapewnienia bezpiecze\u0144stwa i optymalizacji)."}, {"lectures": 30, "name": "Seminarium: Bezpiecze\u0144stwo i ochrona informacji", "entity": 127, "semester": 1, "exercises": 0, "laboratories": 0, "type": 7, "slug": "seminarium-bezpieczenstwo-i-ochrona-informacji", "description": "Opis"}, {"lectures": 45, "name": "Algebra",  "entity": 128, "semester": 2, "exercises": 30, "laboratories": 0, "type": 1, "slug": "algebra", "description": "   1. Grupy i grupy permutacji. Podstawowe poj\u0119cia: rz\u0105d grupy, rz\u0105d elementu grupy, podgrupa. Grupy permutacji. Rozk\u0142ad permutacji na cykle. Znak permutacji.\r\n   2. Homomorfizmy grup. Kongruencje, dzielniki normalne, grupy ilorazowe, wzmianka o algebrach pocz\u0105tkowych.\r\n   3. Zagadnienia kombinatoryczne. Twierdzenie Lagrange'a, orbity i stabilizatory, dzia\u0142anie grupy na zbiorze, lemat Bernsteina.\r\n   4. Arytmetyka modularna. Relacja podzielno\u015bci. Pier\u015bcienie i pier\u015bcienie Z_n. Algorytm Euklidesa, chi\u0144skie twierdzenie o resztach, w\u0142asno\u015bci grup cyklicznych.\r\n   5. Wielomiany. Pier\u015bcienie wielomian\u00f3w. Podzielno\u015b\u0107 wielomian\u00f3w. Przyk\u0142ad konstrukcji cia\u0142a sko\u0144czonego. Cykliczno\u015b\u0107 grupy multiplikatywnej cia\u0142a sko\u0144czonego.\r\n   6. Przestrzenie liniowe i moduly. Zbiory liniowo niezale\u017cne. Bazy. Macierze i przekszta\u0142cenia liniowe. Rz\u0105d macierzy. Algorytm eliminacji Gaussa.\r\n   7. Wyznaczniki. W\u0142asno\u015bci wyznacznik\u00f3w. Rozwiniecie Laplace'a.\r\n   8. R\u00f3wnania liniowe. Zbi\u00f3r rozwiaz\u0105\u0144 uk\u0142adu r\u00f3wna\u0144 liniowych. Dope\u0142nienie ortogonalne podprzestrzeni. Wzory Cramera.\r\n   9. Elementy geometrii. Iloczyn skalarny. Odleg\u0142o\u015b\u0107 punkt\u00f3w. R\u00f3wnania prostych i p\u0142aszczyzn. Izometrie i przekszta\u0142cenia ortogonalne. Wielomian charakterystyczny. Obroty. Wzmianka o kwaternionach.\r\n  10. Nier\u00f3wnosci liniowe. Lemat Farkasa. Zbi\u00f3r rozwiaza\u0144 uk\u0142adu nier\u00f3wno\u015bci liniowych a uwypukleniem zbioru rozwi\u0105za\u0144 bazowych.\r\n  11. Formy dwuliniowe i kwadratowe. R\u00f3wnowazne formy kwadratowe (w pe\u0142nej grupie przekszta\u0142ce\u0144 i grupie ortogonalnej). Metoda Lagrange'a sprowadzania formy kwadratowej do postaci kanonicznej. Sprowadzanie formy kwadratowej do postaci kanonicznej w grupie ortogonalnej."
}, {"lectures": 30, "name": "Zastosowanie teorii kategorii do konstruowania program\u00f3w", "entity": 129, "semester": 1, "exercises": 30, "laboratories": 0, "type": 5, "slug": "zastosowanie-teorii-kategorii-do-konstruowania-programow", "description": "Opis"}, ]

# SETUP
file_input = 'static_data.json'
file_output = 'new_initial_data.json'

# students
NUM_OF_STUDENTS = 500
ECTS_LOW = 0
ECTS_HIGH = 300
DELAY_MINUTES_FOR_STUDENT_LOW = 0
DELAY_MINUTES_FOR_STUDENT_HIGH = 3 * 24 * 60
STUDIES_PROGRAMS = [1, 2] 

# employees
NUM_OF_EMPLOYEES = 50

#classrooms
NUM_OF_CLASSROOMS = 30
CLASSROOMS_NUMBERS = [i for i in range(1, 150)]

#groups
MIN_NON_LECTURE_GROUPS_FOR_SUBJECT = 1
MAX_NON_LECTURE_GROUPS_FOR_SUBJECT = 5
LECTURES_LIMITS = [20, 30, 40, 50, 60, 100, 200]
NON_LECTURE_LIMITS = [20, 30]

#students_options 
DELAY_MINUTES_FOR_SUBJECT_LOW = 0
DELAY_MINUTES_FOR_SUBJECT_HIGH = 3 * 24 * 60
#records
NUM_OF_RECORDS = 3000

INDENT = 4

MALE_FIRST_NAMES = ['Adam', 'Adolf', 'Adrian', 'Albert', 'Albin', 'Aleksander', 'Aleksy', 'Alfons', 'Alfred', 'Alojzy', 'Ambroży', 'Anatol', 'Andrzej', 'Antoni', 'Anzelm', 'Apolinary', 'Arkadiusz', 'Artur', 'August', 'Augustyn', 'Bartłomiej', 'Bazyli', 'Benedykt', 'Bernard', 'Błażej', 'Bogdan', 'Bogumił', 'Bogusław', 'Bolesław', 'Bonifacy', 'Borys', 'Bronisław', 'Cezary', 'Cyprian', 'Cyryl', 'Czesław', 'Damazy', 'Damian', 'Daniel', 'Dariusz', 'Dawid', 'Dionizy', 'Dominik', 'Edmund', 'Edward', 'Edwin', 'Eligiusz', 'Erazm', 'Ernest', 'Eryk', 'Eugeniusz', 'Eustachy', 'Euzebiusz', 'Felicjan', 'Feliks', 'Ferdynand', 'Filip', 'Florian', 'Franciszek', 'Fryderyk', 'Gabriel', 'Gerard', 'Gerwazy', 'Grzegorz', 'Gustaw', 'Henryk', 'Herbert', 'Hieronim', 'Hilary', 'Hubert', 'Hugon', 'Ignacy', 'Ireneusz', 'Iwo', 'Izydor', 'Jacek', 'Jakub', 'Jan', 'Jaromir', 'Jarosław', 'Jerzy', 'Józef', 'Julian', 'Juliusz', 'Justyn', 'Kajetan', 'Kalikst', 'Kamil', 'Karol', 'Kasper', 'Kazimierz', 'Klemens', 'Konrad', 'Krzysztof', 'Lech', 'Leon', 'Leonard', 'Leopold', 'Leszek', 'Lubomir', 'Lucjan', 'Ludwik', 'łukasz', 'Maciej', 'Maksymilian', 'Marcin', 'Marek', 'Marian', 'Mariusz', 'Mateusz', 'Maurycy', 'Michał', 'Mieczysław', 'Mikołaj', 'Miłosz', 'Mirosław', 'Nikodem', 'Norbert', 'Olaf', 'Olgierd', 'Oskar', 'Otton', 'Pankracy', 'Patryk', 'Paweł', 'Piotr', 'Polikarp', 'Protazy', 'Przemysław', 'Radosław', 'Rafał', 'Rajmund', 'Remigiusz', 'Robert', 'Roman', 'Rudolf', 'Rupert', 'Ryszard', 'Sebastian', 'Sergiusz', 'Seweryn', 'Sławomir', 'Sobiesław', 'Stanisław', 'Stefan', 'Sylwester', 'Szczepan', 'Szymon', 'Tadeusz', 'Teodor', 'Teofil', 'Tomasz', 'Tytus', 'Urban', 'Wacław', 'Waldemar', 'Walenty', 'Walery', 'Wawrzyniec', 'Wiesław', 'Wiktor', 'Wilhelm', 'Wincenty', 'Wit', 'Witold', 'Władysław', 'Włodzimierz', 'Wojciech', 'Wolfgang', 'Zbigniew', 'Zdzisław', 'Zenobiusz', 'Zenon', 'Zygmunt', ]

FEMALE_FIRST_NAMES = ['Adela', 'Adelajda', 'Agata', 'Agnieszka', 'Aldona', 'Aleksandra', 'Alicja', 'Alina', 'Amalia', 'Anastazja', 'Aniela', 'Anna', 'Antonina', 'Apolonia', 'Aurelia', 'Balbina', 'Barbara', 'Beata', 'Bernadeta', 'Berta', 'Blanka', 'Bogumiła', 'Bronisława', 'Brygida', 'Cecylia', 'Celina', 'Czesława', 'Danuta', 'Diana', 'Dominika', 'Dorota', 'Edyta', 'Eleonora', 'Elżbieta', 'Emilia', 'Ernestyna', 'Estera', 'Eufemia', 'Eugenia', 'Eulalia', 'Ewa', 'Ewelina', 'Faustyna', 'Felicja', 'Filomena', 'Florentyna', 'Franciszka', 'Genowefa', 'Gertruda', 'Grażyna', 'Halina', 'Helena', 'Henryka', 'Honorata', 'Hortensja', 'Ida', 'Irena', 'Iwona', 'Izabela', 'Jadwiga', 'Janina', 'Joanna', 'Jolanta', 'Józefa', 'Judyta', 'Julia', 'Justyna', 'Kamila', 'Karina', 'Karolina', 'Katarzyna', 'Kinga', 'Klara', 'Klementyna', 'Klotylda', 'Konstancja', 'Kornelia', 'Krystyna', 'Kunegunda', 'Laura', 'Leokadia', 'Leontyna', 'Lidia', 'Liliana', 'Lucyna', 'Ludmiła', 'Ludwika', 'łucja', 'Magdalena', 'Małgorzata', 'Marcelina', 'Marcjanna', 'Maria', 'Marta', 'Matylda', 'Melania', 'Michalina', 'Monika', 'Natalia', 'Nina', 'Olga', 'Olimpia', 'Otylia', 'Patrycja', 'Paulina', 'Pelagia', 'Petronela', 'Pulcheria', 'Prakseda', 'Rachela', 'Regina', 'Romana', 'Rozalia', 'Róża', 'Sabina', 'Salomea', 'Scholastyka', 'Stanisława', 'Stefania', 'Sylwia', 'Tamara', 'Tekla', 'Teodora', 'Teodozja', 'Teresa', 'Urszula', 'Waleria', 'Wanda', 'Weronika', 'Wiktoria', 'Władysława', 'Zdzisława', 'Zofia', 'Zuzanna', 'Zyta', ]

MALE_LAST_NAMES = ['Nowak', 'Kowalski', 'Wiśniewski', 'Dąbrowski', 'Lewandowski', 'Wójcik', 'Kamiński', 'Kowalczyk', 'Zieliński', 'Szymański', 'Woźniak', 'Kozłowski', 'Jankowski', 'Wojciechowski', 'Kwiatkowski', 'Kaczmarek', 'Mazur', 'Krawczyk', 'Piotrowski', 'Grabowski', 'Nowakowski', 'Pawłowski', 'Michalski', 'Nowicki', 'Adamczyk', 'Dudek', 'Zając', 'Wieczorek', 'Jabłoński', 'Król', 'Majewski', 'Olszewski', 'Jaworski', 'Wróbel', 'Malinowski', 'Pawlak', 'Witkowski', 'Walczak', 'Stępień', 'Górski', 'Rutkowski', 'Michalak', 'Sikora', 'Ostrowski', 'Baran', 'Duda', 'Szewczyk', 'Tomaszewski', 'Pietrzak', 'Marciniak', 'Wróblewski', 'Zalewski', 'Jakubowski', 'Jasiński', 'Zawadzki', 'Sadowski', 'Bąk', 'Chmielewski', 'Włodarczyk', 'Borkowski', 'Czarnecki', 'Sawicki', 'Sokołowski', 'Urbański', 'Kubiak', 'Maciejewski', 'Szczepański', 'Kucharski', 'Wilk', 'Kalinowski', 'Lis', 'Mazurek', 'Wysocki', 'Adamski', 'Kaźmierczak', 'Wasilewski', 'Sobczak', 'Czerwiński', 'Andrzejewski', 'Cieślak', 'Głowacki', 'Zakrzewski', 'Kołodziej', 'Sikorski', 'Krajewski', 'Gajewski', 'Szymczak', 'Szulc', 'Baranowski', 'Laskowski', 'Brzeziński', 'Makowski', 'Ziółkowski', 'Przybylski', 'Domański', 'Nowacki', 'Borowski', 'Błaszczyk', 'Chojnacki', 'Ciesielski', 'Mróz', 'Szczepaniak', 'Wesołowski', 'Górecki', 'Krupa', 'Kaczmarczyk', 'Leszczyński', 'Lipiński', 'Kowalewski', 'Urbaniak', 'Kozak', 'Kania', 'Mikołajczyk', 'Czajkowski', 'Mucha', 'Tomczak', 'Kozioł', 'Markowski', 'Kowalik', 'Nawrocki', 'Brzozowski', 'Janik', 'Musiał', 'Wawrzyniak', 'Markiewicz', 'Orłowski', 'Tomczyk', 'Jarosz', 'Kołodziejczyk', 'Kurek', 'Kopeć', 'Żak', 'Wolski', 'Łuczak', 'Dziedzic', 'Kot', 'Stasiak', 'Stankiewicz', 'Piątek', 'Jóźwiak', 'Urban', 'Dobrowolski', 'Pawlik', 'Kruk', 'Domagała', 'Piasecki', ]

FEMALE_LAST_NAMES = ['Nowak', 'Kowalska', 'Wiśniewska', 'Dąbrowska', 'Lewandowska', 'Wójcik', 'Kamińska', 'Kowalczyk', 'Zielińska', 'Szymańska', 'Woźniak', 'Kozłowska', 'Jankowska', 'Wojciechowska', 'Kwiatkowska', 'Kaczmarek', 'Mazur', 'Krawczyk', 'Piotrowska', 'Grabowska', 'Nowakowska', 'Pawłowska', 'Michalska', 'Nowicka', 'Adamczyk', 'Dudek', 'Zając', 'Wieczorek', 'Jabłońska', 'Król', 'Majewska', 'Olszewska', 'Jaworska', 'Wróbel', 'Malinowska', 'Pawlak', 'Witkowska', 'Walczak', 'Stępień', 'Górska', 'Rutkowska', 'Michalak', 'Sikora', 'Ostrowska', 'Baran', 'Duda', 'Szewczyk', 'Tomaszewska', 'Pietrzak', 'Marciniak', 'Wróblewska', 'Zalewska', 'Jakubowska', 'Jasińska', 'Zawadzka', 'Sadowska', 'Bąk', 'Chmielewska', 'Włodarczyk', 'Borkowska', 'Czarnecka', 'Sawicka', 'Sokołowska', 'Urbańska', 'Kubiak', 'Maciejewska', 'Szczepańska', 'Kucharska', 'Wilk', 'Kalinowska', 'Lis', 'Mazurek', 'Wysocka', 'Adamska', 'Kaźmierczak', 'Wasilewska', 'Sobczak', 'Czerwińska', 'Andrzejewska', 'Cieślak', 'Głowacka', 'Zakrzewska', 'Kołodziej', 'Sikorska', 'Krajewska', 'Gajewska', 'Szymczak', 'Szulc', 'Baranowska', 'Laskowska', 'Brzezińska', 'Makowska', 'Ziółkowska', 'Przybylska', 'Domańska', 'Nowacka', 'Borowska', 'Błaszczyk', 'Chojnacka', 'Ciesielska', 'Mróz', 'Szczepaniak', 'Wesołowska', 'Górecka', 'Krupa', 'Kaczmarczyk', 'Leszczyńska', 'Lipińska', 'Kowalewska', 'Urbaniak', 'Kozak', 'Kania', 'Mikołajczyk', 'Czajkowska', 'Mucha', 'Tomczak', 'Kozioł', 'Markowska', 'Kowalik', 'Nawrocka', 'Brzozowska', 'Janik', 'Musiał', 'Wawrzyniak', 'Markiewicz', 'Orłowska', 'Tomczyk', 'Jarosz', 'Kołodziejczyk', 'Kurek', 'Kopeć', 'Żak', 'Wolska', 'Łuczak', 'Dziedzic', 'Kot', 'Stasiak', 'Stankiewicz', 'Piątek', 'Jóźwiak', 'Urban', 'Dobrowolska', 'Pawlik', 'Kruk', 'Domagała', 'Piasecka', ]

# BEGIN SCRIPT

spaces = ' ' * INDENT
s = ""

# Read static data and write it to begin of output
f_input = open(file_input, 'r')
input_data = f_input.read()
input_data = input_data[:-2] + ',\n'
s += input_data
# Generate users
id_start = 2

# Generate users for student
username = 2
first_user_for_student_id = id_start
for user_id in range(id_start, id_start + NUM_OF_STUDENTS):
	if user_id % 2:
		first_name = choice(MALE_FIRST_NAMES)
		last_name = choice(MALE_LAST_NAMES)
	else:
		first_name = choice(FEMALE_FIRST_NAMES)
		last_name = choice(FEMALE_LAST_NAMES)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "auth.user",\n@!@@!@"fields": {\n@!@@!@@!@"username": "%s",\n@!@@!@@!@"first_name": "%s",\n@!@@!@@!@"last_name": "%s",\n@!@@!@@!@"is_active": true,\n@!@@!@@!@"is_superuser": false,\n@!@@!@@!@"is_staff": false,\n@!@@!@@!@"last_login": "2010-11-04 14:43:11",\n@!@@!@@!@"groups": [],\n@!@@!@@!@"user_permissions": [],\n@!@@!@@!@"password": "sha1$9915f$38f8781f7fbaed11078a9f38295b7bea1f871cb7",\n@!@@!@@!@"email": "%s.%s@fereol.pl",\n@!@@!@@!@"date_joined": "2010-11-04 14:42:09"\n@!@@!@}\n@!@},\n' % (user_id, username, first_name, last_name, first_name.lower(), last_name.lower())
	record = record.replace('@!@', spaces)
	s += record
	username += 1
last_user_for_student_id = user_id

# Generate users for employees
first_user_for_employee_id = id_start + NUM_OF_STUDENTS
for user_id in range(id_start + NUM_OF_STUDENTS, id_start + NUM_OF_STUDENTS + NUM_OF_EMPLOYEES):
	if user_id % 2:
		first_name = choice(MALE_FIRST_NAMES)
		last_name = choice(MALE_LAST_NAMES)
	else:
		first_name = choice(FEMALE_FIRST_NAMES)
		last_name = choice(FEMALE_LAST_NAMES)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "auth.user",\n@!@@!@"fields": {\n@!@@!@@!@"username": "%s",\n@!@@!@@!@"first_name": "%s",\n@!@@!@@!@"last_name": "%s",\n@!@@!@@!@"is_active": true,\n@!@@!@@!@"is_superuser": false,\n@!@@!@@!@"is_staff": false,\n@!@@!@@!@"last_login": "2010-11-04 14:43:11",\n@!@@!@@!@"groups": [],\n@!@@!@@!@"user_permissions": [],\n@!@@!@@!@"password": "sha1$9915f$38f8781f7fbaed11078a9f38295b7bea1f871cb7",\n@!@@!@@!@"email": "%s.%s@fereol.pl",\n@!@@!@@!@"date_joined": "2010-11-04 14:42:09"\n@!@@!@}\n@!@},\n' % (user_id, username, first_name, last_name, first_name.lower(), last_name.lower())
	s += record
	username += 1
last_user_for_employee_id = user_id

# Generate classrooms
classroom_id_start = 1
classrooms = []
for classroom_id in range(classroom_id_start, classroom_id_start + NUM_OF_CLASSROOMS):
	number = choice(CLASSROOMS_NUMBERS)
	while number in classrooms:
		number = choice(CLASSROOMS_NUMBERS)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.classroom",\n@!@@!@"fields": {\n@!@@!@@!@"number": "%s"\n@!@@!@}\n@!@},\n' % (classroom_id, number)
	s += record
classroom_id_end = classroom_id
# Generate students

for student_id in range(first_user_for_student_id, last_user_for_student_id + 1):
	ects = rand(ECTS_LOW, ECTS_HIGH)
	delay = rand(DELAY_MINUTES_FOR_STUDENT_LOW, DELAY_MINUTES_FOR_STUDENT_HIGH)
	program = choice(STUDIES_PROGRAMS)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "users.student",\n@!@@!@"fields": {\n@!@@!@@!@"ects": %s,\n@!@@!@@!@"records_opening_delay_minutes": %s,\n@!@@!@@!@"receive_mass_mail_offer": true,\n@!@@!@@!@"user": %s,\n@!@@!@@!@"matricula": "%s",\n@!@@!@@!@"program": %s,\n@!@@!@@!@"receive_mass_mail_enrollment": true\n@!@@!@}\n@!@},\n' % (student_id, ects, delay, student_id, student_id, program)
	s += record
	
# Generate employees

for employee_id in range(first_user_for_employee_id, last_user_for_employee_id + 1):
	ects = rand(ECTS_LOW, ECTS_HIGH)
	delay = rand(DELAY_MINUTES_FOR_STUDENT_LOW, DELAY_MINUTES_FOR_STUDENT_HIGH)
	program = choice(STUDIES_PROGRAMS)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "users.employee",\n@!@@!@"fields": {\n@!@@!@@!@"consultations": "pn 10:00 - 12:00",\n@!@@!@@!@"receive_mass_mail_offer": true,\n@!@@!@@!@"user": %s,\n@!@@!@@!@"receive_mass_mail_enrollment": true\n@!@@!@}\n@!@},\n' % (employee_id, employee_id)
	s += record

# Generate subjects

subject_id_start = 1
subject_id = subject_id_start
# Generate subjects in year 2009
for sub in SUBJECTS:
	if sub['semester'] == 1:
		slug = '%s-zimowy-2009' % (sub['slug'])
	else:
		slug = '%s-letni-2009' % (sub['slug'])
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.subject",\n@!@@!@"fields": {\n@!@@!@@!@"lectures": %s,\n@!@@!@@!@"name": "%s",\n@!@@!@@!@"entity": %s,\n@!@@!@@!@"semester": %s,\n@!@@!@@!@"exercises": %s,\n@!@@!@@!@"laboratories": %s,\n@!@@!@@!@"type": %s,\n@!@@!@@!@"slug": "%s",\n@!@@!@@!@"description": "Opis"\n@!@@!@}\n@!@},\n' % (subject_id, sub['lectures'], sub['name'], sub['entity'], sub['semester'], sub['exercises'], sub['laboratories'], sub['type'], slug)
	s += record
	subject_id += 1
	
# Generate subjects in year 2010
for sub in SUBJECTS[:-2]:
	if sub['semester'] == 1:
		slug = '%s-zimowy-2010' % (sub['slug'])
	else:
		slug = '%s-letni-2010' % (sub['slug'])
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.subject",\n@!@@!@"fields": {\n@!@@!@@!@"lectures": %s,\n@!@@!@@!@"name": "%s",\n@!@@!@@!@"entity": %s,\n@!@@!@@!@"semester": %s,\n@!@@!@@!@"exercises": %s,\n@!@@!@@!@"laboratories": %s,\n@!@@!@@!@"type": %s,\n@!@@!@@!@"slug": "%s",\n@!@@!@@!@"description": "Opis"\n@!@@!@}\n@!@},\n' % (subject_id, sub['lectures'], sub['name'], sub['entity'], sub['semester'] + 2, sub['exercises'], sub['laboratories'], sub['type'], slug)
	s += record
	subject_id += 1
	
subject_id_end = subject_id

# Generate groups 
group_id_start = 1
group_id = group_id_start

for subject_id in range(subject_id_start, subject_id_end):
	teacher = rand(first_user_for_employee_id, last_user_for_employee_id)
	limit = choice(LECTURES_LIMITS)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.group",\n@!@@!@"fields": {\n@!@@!@@!@"limit": %s,\n@!@@!@@!@"type": "1",\n@!@@!@@!@"teacher": %s,\n@!@@!@@!@"subject": %s\n@!@@!@}\n@!@},\n' % (group_id, limit, teacher, subject_id)
	s += record
	group_id += 1
	groups = rand(MIN_NON_LECTURE_GROUPS_FOR_SUBJECT, MAX_NON_LECTURE_GROUPS_FOR_SUBJECT)	
	for i in range(1, groups + 1):
		teacher = rand(first_user_for_employee_id, last_user_for_employee_id)
		limit = choice(NON_LECTURE_LIMITS)
		record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.group",\n@!@@!@"fields": {\n@!@@!@@!@"limit": %s,\n@!@@!@@!@"type": "2",\n@!@@!@@!@"teacher": %s,\n@!@@!@@!@"subject": %s\n@!@@!@}\n@!@},\n' % (group_id, limit, teacher, subject_id)
		s += record
		group_id += 1
		
group_id_end = group_id

# Generate terms

triples = []

for term_id in range(group_id_start, group_id_end):
	day = rand(1, 5)
	classroom = rand(classroom_id_start, classroom_id_end)
	start_hour = 2 * rand(4, 9)
	triple = (day, classroom, start_hour)
	
	while triple in triples:
		day = rand(1, 5)
		classroom = rand(classroom_id_start, classroom_id_end)
		start_hour = 2 * rand(4, 9)
		triple = (day, classroom, start_hour)
	triples.append(triple)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.term",\n@!@@!@"fields": {\n@!@@!@@!@"dayOfWeek": "%s",\n@!@@!@@!@"classroom": %s,\n@!@@!@@!@"start_time": "%s:00:00",\n@!@@!@@!@"group": %s,\n@!@@!@@!@"end_time": "%s:00:00"\n@!@@!@}\n@!@},\n' % (term_id, day, classroom, start_hour, term_id, start_hour + 2)
	s += record

# generate student_options

student_options_id = 1

for student in range(first_user_for_student_id, last_user_for_student_id):
	for subject in range(subject_id_start, subject_id_end):
		delay = rand(DELAY_MINUTES_FOR_SUBJECT_LOW, DELAY_MINUTES_FOR_SUBJECT_HIGH)
		record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "subjects.studentoptions",\n@!@@!@"fields": {\n@!@@!@@!@"records_opening_delay_minutes": %s,\n@!@@!@@!@"student": %s,\n@!@@!@@!@"subject": %s\n@!@@!@}\n@!@},\n' % (student_options_id, delay, student, subject)
		s += record
		student_options_id += 1

#generate_records

pairs = []

counter = 0

for record_id in range(1, NUM_OF_RECORDS + 1):
	group = rand(group_id_start, group_id_end - 1)
	student = rand(first_user_for_student_id, last_user_for_student_id - 1)
	pair = (group, student)
	while pair in pairs:
		group = rand(group_id_start, group_id_end - 1)
		student = rand(first_user_for_student_id, last_user_for_student_id - 1)
		pair = (group, student)
		counter += 1
		print counter
		print "losuje: g=%s, s=%s" % (group, student)
	counter = 0
	pairs.append(pair)
	record = '@!@{\n@!@@!@"pk": %s,\n@!@@!@"model": "records.record",\n@!@@!@"fields": {\n@!@@!@@!@"status": "1",\n@!@@!@@!@"group": %s,\n@!@@!@@!@"student": %s\n@!@@!@}\n@!@},\n' % (record_id, group, student)
	s += record
	
# Convert to readable format using indents and add close bracket
s = s.replace('@!@', spaces)
s = s[:-2]
s = s + '\n]'

# Write to output file
f_output = open(file_output, 'w')
f_output.write(s)
f_output.close()