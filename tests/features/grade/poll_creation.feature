Feature: User with privileges wants to create a poll.

    Scenario: First preparations
        Given I start new scenario for "grade"
        And there are some courses with groups for current semester
        And there are some sections created already
        And the grading protocol is "off"
        
    Scenario: Administrator can see all the courses
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I press "Utwórz nową"
        Then I can select from "4" options in "Przedmiot: "
                    
    Scenario: Employee can see only his courses
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I press "Utwórz nową"
        Then I can select from "3" options in "Przedmiot: "
        And I can select "Przedmiot 1" as "Przedmiot: "
        And I can select "Przedmiot 3" as "Przedmiot: "
        And I can select "Przedmiot 4" as "Przedmiot: "
            
    Scenario: Administrator can only see types of groups for which there are some groups
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I press "Utwórz nową"
        And I select "Przedmiot: " as "Przedmiot 1"
        Then I can select from "2" options in "Typ zajęć: "
        And I can select "wykład" as "Typ zajęć: "
        And I can select "ćwiczenia" as "Typ zajęć: "
        
    Scenario: Administrator cannot add the same section twice in a poll
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"
        And I select "Wybierz sekcję: " as "Ogół zajęć"
        And I press "Dodaj sekcję"
        Then I can not select "Ogół zajęć" from "Wybierz sekcję: "
            
    @TODO
    Scenario: Employee creates a poll for his course for all exercises groups
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I press "Utwórz nową"
        And I select "Przedmiot: " as "Przedmiot 1"
        And I select "Typ zajęć: " as "ćwiczenia"
        And I fill in "Tytuł: " with "Ankieta dla ćwiczeń z przedmiotu 1"
        And I select "Wybierz sekcję: " as "Ćwiczenia"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"   
        Then I should see "Utworzono ankiety"
        #And I should see "Liczba utworzonych ankiet: 3"
            
    Scenario: Employee creates a poll for his course, just for lecture
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"
        And I select "Przedmiot: " as "Przedmiot 1"
        And I select "Typ zajęć: " as "wykład"
        And I fill in "Tytuł: " with "Ankieta dla wykładu z przedmiotu 1"
        And I select "Wybierz sekcję: " as "Wykład"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 1"        
                
    Scenario: Employee creates a poll for his group, when he is not the lecturer
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"
        And I select "Przedmiot: " as "Przedmiot 2"
        And I select "Typ zajęć: " as "ćwiczenia"
        And I select "Grupa: " as "Pracownik Testowy"
        And I fill in "Tytuł: " with "Ankieta dla ćwiczeń z przedmiotu 1"
        And I select "Wybierz sekcję: " as "Ćwiczenia"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 1"            
            
    Scenario: Administrator creates a poll with no course or group assigned
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"
        And I fill in "Tytuł: " with "Ogół zajęć w instytucie"
        And I select "Wybierz sekcję: " as "Ogół zajęć"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Trwa generowanie kluczy"
        And I wait for a while to see "100 %"
        When I click "generowanie"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 1"    
    
    Scenario: Administrator creates a poll for every lecture there is
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"   
        And I fill in "Tytuł: " with "Ankieta do wykładu"
        And I select "Przedmiot: " as "Wszystkie przedmioty"
        And I select "Typ zajęć: " as "wykład"        
        And I select "Wybierz sekcję: " as "Wykład"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Trwa generowanie kluczy"
        And I wait for a while to see "100 %"
        When I click "generowanie"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 4"
            
    @TODO
    Scenario: Administrator creates a poll for exercises for a specific lecture
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"    
        And I fill in "Tytuł: " with "Ankieta do ćwiczeń do przedmiotu 4"
        And I select "Przedmiot: " as "Przedmiot 4"
        And I select "Typ zajęć: " as "ćwiczenia"        
        And I select "Wybierz sekcję: " as "Ćwiczenia"
        And I press "Dodaj sekcję"        
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Trwa generowanie kluczy"
        And I wait for a while to see "100 %"
        When I click "generowanie"
        Then I should see "Utworzono ankiety"
        #And I should see "Liczba utworzonych ankiet: 2"    

    Scenario: Administrator creates a poll for all the lectures, available only to students on 'studia licencjackie'
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową" 
        And I fill in "Tytuł: " with "Ankieta do wykładu, studia licencjackie"
        And I select "Przedmiot: " as "Wszystkie przedmioty"
        And I select "Typ zajęć: " as "wykład"
        And I select "Typ studiów: " as "licencjackie"
        And I select "Wybierz sekcję: " as "Wykład"
        And I press "Dodaj sekcję"        
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Trwa generowanie kluczy"
        And I wait for a while to see "100 %"
        When I click "generowanie"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 4" 
    
    @TODO
    Scenario: Employee can not create a poll for somebody elses group when he is not a lecturer - but he can for his own
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I press "Utwórz nową"
        And I select "Przedmiot: " as "Przedmiot 2"
        And I select "Typ zajęć: " as "ćwiczenia"
        And I fill in "Tytuł: " with "Ankieta dla ćwiczeń z przedmiotu 1"
        And I select "Wybierz sekcję: " as "Ćwiczenia"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Utworzono ankiety"        
        #And I should see "Liczba utworzonych ankiet: 1"

    Scenario: Administrator fails to create a poll when there is no title
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "To pole jest wymagane"
            
    Scenario: Administrator fails to create a poll when there are no sections
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"
        And I fill in "Tytuł: " with "Ankieta bez treści"
        And I press "Stwórz ankietę"
        Then I wait for a while to see "Nie można utworzyć ankiety; ankieta jest pusta"            
        
    Scenario: Administrator creates a poll for all the exercises when there is already a poll for some exercises
        Given I start new scenario for "grade"
        And there are some courses with groups for current semester
        And there are some sections created already
        And the grading protocol is "off"
        And there is a poll for some exercises
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"      
        And I fill in "Tytuł: " with "Ankieta do ćwiczeń"
        And I select "Przedmiot: " as "Wszystkie przedmioty"
        And I select "Typ zajęć: " as "ćwiczenia"        
        And I select "Wybierz sekcję: " as "Ćwiczenia"
        And I press "Dodaj sekcję"        
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Trwa generowanie kluczy"
        And I wait for a while to see "100 %"
        When I click "generowanie"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 8"
            
    Scenario: Administrator creates a poll for all the exercises without polls
        Given I start new scenario for "grade"
        And there are some courses with groups for current semester
        And there are some sections created already     
        And the grading protocol is "off"
        And there is a poll for some exercises
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I press "Utwórz nową"      
        And I fill in "Tytuł: " with "Ankieta do ćwiczeń"
        And I select "Przedmiot: " as "Wszystkie przedmioty"
        And I select "Typ zajęć: " as "ćwiczenia"      
        And I check "Utwórz tylko dla grup bez ankiet"  
        And I select "Wybierz sekcję: " as "Ćwiczenia"
        And I press "Dodaj sekcję"        
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz ankietę"
        Then I should see "Trwa generowanie kluczy"
        And I wait for a while to see "100 %"
        When I click "generowanie"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 6"   
                        
    Scenario: Administrator fails to create a poll when the grading protocol is on
        Given I start new scenario for "grade"
        And the grading protocol is "on"
        And I am logged in with "administrator" privileges
        And I am on grade main page 
        When I go to /grade/poll/managment/poll_create
        Then I wait for a while to see "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona" 
        
