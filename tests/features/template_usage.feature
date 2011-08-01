Feature: User with privileges wants to delete some templates.

    Scenario: Preparations
        Given I start new scenario
        And the grading protocol is "off"
        And there are templates generated
       
    @TODO
    Scenario: Administrator uses template to create polls
        Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista szablonów" 
        And I check "_selected_action" with value "1" 
        And I select "action" as "Zastosuj wybrane szablony"
        And I press "Wykonaj"		
        And I press "Zastosuj"
		#Then I should see "Trwa generowanie kluczy"
        #And I wait for a while to see "100 %"
        #When I click "generowanie"
        Then I should see "Utworzono ankiety"
        And I should see "Liczba utworzonych ankiet: 4"   
