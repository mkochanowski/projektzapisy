Feature: User with privileges wants to delete some polls.

    Background:
        Given I start new scenario
        And the grading protocol is "off"
		And there are polls generated
		And there are keys generated for polls        

    Scenario: Administrator deletes a poll
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet"
        And I check "_selected_action" with value "13" 
        And I select "action" as "Usuń wybrane ankiety"
        And I press "Wykonaj"
        Then I should see "Usunięto 1 ankietę"
    
    Scenario: Administrator deletes all polls
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet"
        And I check "action-toggle" 
        And I select "action" as "Usuń wybrane ankiety"
        And I press "Wykonaj"
        Then I should see "Usunięto 13 ankiet"
                        
    Scenario: Employee deletes his own poll
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet"
        And I check "_selected_action" with value "1"
        And I select "action" as "Usuń wybrane ankiety"
        And I press "Wykonaj"
        Then I should see "Usunięto 1 ankietę"        
        
    Scenario: Employee deletes all his polls
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet"
        And I check "action-toggle"    
        And I select "action" as "Usuń wybrane ankiety"
        And I press "Wykonaj"
        Then I should see "Usunięto 2 ankiety"
