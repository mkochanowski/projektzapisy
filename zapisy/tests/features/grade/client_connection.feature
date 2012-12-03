Feature: User downloads tickets using supplied external client.

    Background:
        Given I start new scenario for "grade"
        And there are polls generated 
        And there are keys generated for polls
        And the grading protocol is "on"
        And I am signed for groups with polls
        
    Scenario: Non downloaded tickets should be downloadable
        Given I am logged in with "student" privileges  
        And I am on grade main page
        And I follow "Pobierz bilety"
        When I run client with "no_tickets_downloaded"
        And I press "Pobierz bilety"
        Then I wait for a while to see "Pomyślnie wygenerowano bilety"
        And I should not see "Bilet już pobrano"
        
    Scenario: Downloaded ticket should not be downloadable
        Given I am logged in with "student" privileges  
        And I am on grade main page
        And I follow "Pobierz bilety"
        When I run client with "ticket_downloaded"
        And I press "Pobierz bilety"
        Then I wait for a while to see "Pomyślnie wygenerowano bilety"
        And I should see "Ankieta: Ankieta ogólna"
        And I should see "Bilet już pobrano"
        
    Scenario: Part of grouping downloaded by client grouping selected in fereol
        Given I am logged in with "student" privileges  
        And I am on grade main page
        And I follow "Pobierz bilety"
        When I run client with "part_of_grouping_downloaded"
        And I press "Pobierz bilety"
        Then I wait for a while to see "Pomyślnie wygenerowano bilety"
        And I should see "Ankieta: Ankieta wykładu, Przedmiot 1: wykład - Pracownik Testowy"
        And I should see "Bilet już pobrano"
        And tickets should not be connected
        
    Scenario: Tickets downloaded in fereol are not downloadable
        Given I am logged in with "student" privileges  
        And I am on grade main page
        And I follow "Pobierz bilety"
        And I press "Pobierz bilety"
        And I wait for a while to see "Pomyślnie wygenerowano bilety"
        When I run client with "ticket_downloaded"
        Then tickets file should not exist
        
    Scenario: Downloaded tickets should enable poll filling
        Given I am on grade main page
        And I follow "Oceń zajęcia"
        When I run client with "ticket_downloaded"
        And I enter generated ticket
        And I press "Wyślij"         
        Then I should see "Twoje ankiety"
        And I should see "Ankiety dostępne"
        And I should see "Ankieta ogólna"
        And I should not see "Nie udało się zweryfikować podpisu pod biletem."
