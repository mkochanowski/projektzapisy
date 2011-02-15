Feature: User with privileges wants to create a poll.

    Background:
        Given I start new scenario
        And there are some subjects with groups for current semester
        And there are some sections created already
        
    Scenario: Employee creates a poll for his subject for all exercises groups
		Given the grading protocol is "off"
        And I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie ankiet"
        And I select "Przedmiot:" as "Przedmiot 1"
        And I select "Typ zajęć:" as "ćwiczenia"
        And I fill in "Tytuł:" as "Ankieta dla ćwiczeń z przedmiotu 1"
        And I select "Wybierz sekcję:" as "Ćwiczenia"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 3"
            
    Scenario: Employee creates a poll for his subject, just for lecture
		Given the grading protocol is "off"
        And I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet"
        And I select "Przedmiot:" as "Przedmiot 1"
        And I select "Typ zajęć:" as "wykład"
        And I fill in "Tytuł:" as "Ankieta dla wykładu z przedmiotu 1"
        And I select "Wybierz sekcję:" as "Wykład"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 1"        
                
    Scenario: Employee creates a poll for his group, when he is not the lecturer
		Given the grading protocol is "off"
        And I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet"
        And I select "Przedmiot:" as "Przedmiot 2"
        And I select "Typ zajęć:" as "ćwiczenia"
        And I select "Grupa:" as "employee-test"
        And I fill in "Tytuł:" as "Ankieta dla ćwiczeń z przedmiotu 1"
        And I select "Wybierz sekcję:" as "Ćwiczenia"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 1"
            
            
    Scenario: Administrator creates a poll with no subject or group assigned
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet"
        And I fill in "Tytuł:" as "Ogół zajęć w instytucie"
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 1"    
    
    Scenario: Administrator creates a poll for every lecture there is
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet"    
        And I fill in "Tytuł:" as "Ankieta do wykładu"
        And I select "Przedmiot:" as "Wszystkie przedmioty"
        And I select "Typ zajęć:" as "wykład"        
        And I select "Wybierz sekcję:" as "Wykład"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 4"
            
    Scenario: Administrator creates a poll for exercises for a specific lecture
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet        
        And I fill in "Tytuł:" as "Ankieta do ćwiczeń do przedmiotu 4"
        And I select "Przedmiot:" as "Przedmiot 4"
        And I select "Typ zajęć:" as "ćwiczeani"        
        And I select "Wybierz sekcję:" as "Ćwiczenia"
        And I press "Dodaj sekcję"        
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 2"    
            
    Scenario: Administrator creates a poll for all the exercises when there is already a poll for some exercises
		Given the grading protocol is "off"
        And there is a poll for "ćwiczenia" for "Przedmiot 4"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet        
        And I fill in "Tytuł:" as "Ankieta do ćwiczeń"
        And I select "Przedmiot:" as "Wszystkie przedmioty"
        And I select "Typ zajęć:" as "ćwiczenia"        
        And I select "Wybierz sekcję:" as "Ćwiczenia"
        And I press "Dodaj sekcję"        
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 8"
            
    Scenario: Administrator creates a poll for all the exercises without polls
		Given the grading protocol is "off"
        And there is a poll for "ćwiczenia" for "Przedmiot 4"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet        
        And I fill in "Tytuł:" as "Ankieta do ćwiczeń"
        And I select "Przedmiot:" as "Wszystkie przedmioty"
        And I select "Typ zajęć:" as "ćwiczenia"      
        And I check "Utwórz dla grup bez ankiet"  
        And I select "Wybierz sekcję:" as "Ćwiczenia"
        And I press "Dodaj sekcję"        
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 6"   
            
    Scenario: Administrator creates a poll for all the lectures, available only to students on 'studia licecjackie'
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet        
        And I fill in "Tytuł:" as "Ankieta do wykładu, studia licencjackie"
        And I select "Przedmiot:" as "Wszystkie przedmioty"
        And I select "Typ zajęć:" as "wykład"
        And I select "Typ studiów:" as "licencjackie"
        And I select "Wybierz sekcję:" as "Wykład"
        And I press "Dodaj sekcję"        
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 8" 
    
    Scenario: Employee fails to create a poll for somebody elses group when he is not a lecturer
		Given the grading protocol is "off"
        And I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie ankiet"
        And I select "Przedmiot:" as "Przedmiot 2"
        And I select "Typ zajęć:" as "ćwiczenia"
        And I fill in "Tytuł:" as "Ankieta dla ćwiczeń z przedmiotu 1"
        And I select "Wybierz sekcję:" as "Ćwiczenia"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Nie masz uprawnień do stworzenia ankiety dla grupy: employee2"
        And I should see "Liczba utworzonych ankiet: 1"

    Scenario: Administrator fails to create a poll when there is no title
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet"
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Brak tytułu ankiety"
            
    Scenario: Administrator fails to create a poll when there are no sections
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Tworzenie ankiet"
        And I fill in "Tytuł:" with "Ankieta bez treści"
        And I press "Stwórz ankietę"
        Then I should see "Brak tytułu ankiety"            
            
    Scenario: Administrator fails to create a poll when the grading protocol is on
   		Given the grading protocol is "on"
        And I am logged in with "administrator" privileges
        And I am on grade main page 
        When I go to /grade/poll/managment/poll_create
        Then I should see "Ocena zajęć jest aktywna, nie można dodawać ankiet"
        
