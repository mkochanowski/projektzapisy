Feature: User with privileges wants to edit some polls.

	Scenario: Preparations
        Given I start new scenario
        And the grading protocol is "off"
		And there are polls generated
		And there are keys generated for polls 

    Scenario: Administrator edits a poll
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet"
        And I follow "Ankieta wykładu, Przedmiot 2: wykład - Pracownik 2"
        And I press "Edytuj"
        And I select "Wybierz sekcję:" as "Ćwiczenia"
        And I press "Dodaj sekcję"
        And I press "Zmień ankietę"
        Then I should see "Ankieta została zmieniona"
        When I follow "Ankieta wykładu, Przedmiot 2: wykład - Pracownik 2"
        Then I should see "Ćwiczenia"
        
    Scenario: Employee edits his own poll
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet"
        And I follow "Ankieta wykładu, Przedmiot 1: wykład - Pracownik Testowy"
        And I press "Edytuj"
        And I delete "Uwagi" section
        And I press "Zmień ankietę"
        Then I should see "Ankieta została zmieniona"
        When I follow "Ankieta wykładu, Przedmiot 1: wykład - Pracownik Testowy"
        Then I should not see "Uwagi"
        
    Scenario: Employee fails to edit a poll that is not his own
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet"
        And I follow "Ankieta wykładu, Przedmiot 2: wykład - Pracownik 2"
        Then I should not see "Edytuj"
