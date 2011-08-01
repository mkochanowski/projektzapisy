Feature: User with privileges wants to delete some templates.

    Scenario: Preparations
        Given I start new scenario
        And the grading protocol is "off"
        And there are templates generated

    Scenario: Administrator deletes one template
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista szablonów" 
        And I check "_selected_action" with value "1" 
        And I select "action" as "Usuń wybrane szablony"
        And I press "Wykonaj"
        And I press "Usuń"        
        Then I should see "Usunięto 1 szablon"    

    Scenario: Employee fails to delete one template
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista szablonów"   
        Then I cannot check "_selected_action"
         
    @TODO 
    Scenario: Employee fails to delete all templates
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista szablonów"   
        #Then I cannot check "action-toggle"            
    
    Scenario: Administrator deletes all templates
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista szablonów" 
        And I check "action-toggle" 
        And I select "action" as "Usuń wybrane szablony"
        And I press "Wykonaj"
        And I press "Usuń"        
        Then I should see "Usunięto 1 szablon"          
