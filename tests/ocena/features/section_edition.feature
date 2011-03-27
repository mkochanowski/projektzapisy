Feature: User with privileges wants to edit some sections.

    Background:
        Given I start new scenario
        And the grading protocol is "off"
        And there are some sections created already   

    Scenario: Administrator edits a section
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista sekcji"
        And I follow "Uwagi"    
        And I press "Edytuj"
        And I press "Dodaj pytanie"
        And I press "Usuń"
        And I press "Dodaj pytanie"
        And I fill in "poll[question][4][title]" with "Czego było za dużo?"
        And I select "poll[question][4][formtype]" as "Pytanie jednokrotnego wyboru"
        And I press "usuń"
        And I press "Dodaj odpowiedź" 
        And I fill in "poll[question][4][answers][1]" with "Algorytmów"
        And I press "Dodaj odpowiedź" 
        And I fill in "poll[question][4][answers][2]" with "Sieci"
        And I press "Dodaj odpowiedź" 
        And I fill in "poll[question][4][answers][3]" with "Kryptografii"
        And I check "poll[question][4][hasOther]"
        And I press "Gotowe"        
        And I press "Zapisz"
        Then I should see "Zapisano sekcję"
                
    Scenario: Employee fails to edit a section
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista sekcji" 
        And I follow "Uwagi"
        Then "Edytuj" should be invisible
