Feature: Filters in poll management are working properly

    Scenario: Preparations
        Given I start new scenario for "grade"
        And there are templates generated
        And the grading protocol is "off"
    
    @TODO    
    Scenario: There are filters for templates
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista szablonów" 
        #Then I should see "Filtrowanie"
        
    Scenario: There are filters for polls
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet" 
        Then I should see "Filtrowanie"
         
    @TODO   
    Scenario: There are filters for sections
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista sekcji" 
        #Then I should see "Filtrowanie"
    
    @TODO
    Scenario: One can filter by name of template in templates list    
    
    Scenario: One can filter by name of poll in polls list
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet" 
        And I fill in "q" with "ogólna"
        And I press "filtruj" 
        Then I wait for a while to see "1 ankieta"
    
    @TODO    
    Scenario: One can filter by name of section in section list           
    
    @TODO
    Scenario: One can filter by template features
    
    Scenario: One can filter by poll features
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet" 
        And I check "Ankiety utworzone przeze mnie"
        And I select "Typ zajęć:" as "ćwiczenia"
        And I press "filtruj" 
        Then I wait for a while to see "7 ankiet"     
    
    @TODO
    Scenario: One can filter by section features
    
    @TODO
    Scenario: When nothing matches, there is info about it
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista ankiet" 
        And I fill in "q" with "bdghjkptw"
        And I press "filtruj" 
        #Then I wait for a while to see "Do podanego filtra nie pasuje żadna ankieta."
