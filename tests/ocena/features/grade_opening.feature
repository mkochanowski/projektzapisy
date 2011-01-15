Feature: Behaviour of the system when trying to open grading

	Background:
		Given I am logged in with "administrator" privileges
		And the grading protocol is "off"		
		And I am on grade main page


	Scenario: No polls in the system - failure
		When I follow "Otwórz ocenę"	
		Then I should see "Nie można otworzyć oceny; brak ankiet"
		And I should be on grade main page		
		
	Scenario: Not all the polls have keys generated - failure
		Given there are polls generated
		And there are keys generated for polls
		And I add new poll
		When I follow "Otwórz ocenę"		
		Then I should see "Nie można otworzyć oceny; brak kluczy dla ankiet"
		And I should be on grade main page
	
	Scenario: Successfully opening grading
		Given there are polls generated
		And there are keys generated for polls
		When I follow "Otwórz ocenę"
		Then I should see "Ocena zajęć otwarta"
		And I should be on grade main page
