Feature: User with privileges wants to edit some polls.

    Background:
        Given I start new scenario
        And the grading protocol is "off"
		And there are polls generated
		And there are keys generated for polls 

    Scenario: Administrator edits a poll
        # Given I am logged in with "administrator" privileges
        # And I am on grade main page
        # When I follow "Zarządzaj ankietami"
        # And I follow "Lista ankiet"
        # And I follow "Ankieta wykładu...."
        # And I press "Edytuj"
        # And I select "Wybierz sekcję:" as "Ćwiczenia"
        # And I press "Dodaj sekcję"
        # And I press "Zapisz"
        # Then I should see "Trwa generowanie biletów"
        # And I wait for a while to see "100%"
        # When I click "generowanie"
        # Then I should see "Zapisano ankietę"
        # And być może coś jeszcze ciekawego się dzieje
        
    Scenario: Employee edits his own poll
        # Given I am logged in with "employee" privileges
        # And I am on grade main page
        # When I follow "Zarządzaj ankietami"
        # And I follow "Lista ankiet"
        # And I follow "Ankieta wykładu dla przedmiotu 1 tiruriru"
        # And I press "Edytuj"
        # And I delete "Uwagi" section
        # And I press "Zapisz"
        # Then I should see "Trwa generowanie biletów"
        # And I wait for a while to see "100%"
        # When I click "generowanie"
        # Then I should see "Zapisano ankietę"
        # And być może coś jeszcze ciekawego się dzieje    
        
    Scenario: Employee fails to edit a poll that is not his own
        # Given I am logged in with "employee" privileges
        # And I am on grade main page
        # When I follow "Zarządzaj ankietami"
        # And I follow "Lista ankiet"
        # And I follow "Ankieta wykładu nie mojego"
        # Then "Edytuj" "button" should be invisible 
