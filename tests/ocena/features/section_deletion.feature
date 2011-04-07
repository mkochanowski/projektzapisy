Feature: User with privileges wants to delete some sections.

    Background:
        Given I start new scenario
        And the grading protocol is "off"
        And there are some sections created already        

    Scenario: Administrator deletes one section
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista sekcji"
        And I check "_selected_action" with value "1" 
        And I select "action" as "Usuń wybrane sekcje"
        And I press "Wykonaj"
        Then I should see "Usunięto 1 sekcję"    
    
    Scenario: Administrator deletes all sections
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista sekcji"
        And I check "action-toggle" 
        And I select "action" as "Usuń wybrane sekcje"
        And I press "Wykonaj"
        Then I should see "Usunięto 4 sekcje"    
        
    Scenario: Employee fails to delete one section
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista sekcji"  
        Then I cannot check "_selected_action"
          
    Scenario: Employee fails to delete all sections
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista sekcji"  
        Then I cannot check "action-toggle"    
