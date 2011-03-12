Feature: Creating keys for polls in the grading protocol

	Background:
        Given I start new scenario	
	
	Scenario: Successfully creating keys for all the polls
		Given the grading protocol is "off"
		And there are polls generated
		And I am logged in with "administrator" privileges
		And I am on grade main page        
		When I follow "Generuj klucze"		
		Then I wait for a while to see "Wygenerowano klucze RSA"
		And I should be on poll management page
	
	Scenario: Successfully creating additional keys for added polls
		Given the grading protocol is "off"
		And there are polls generated
		And I am logged in with "administrator" privileges
		And I am on grade main page        
		And there are keys generated for polls
		When I add new poll
		And I follow "Generuj klucze"
		Then I wait for a while to see "Wygenerowano klucze RSA"
		And I should be on poll management page
	
	Scenario: Failing to create keys - all the polls already have them
		Given the grading protocol is "off"
		And there are polls generated
		And I am logged in with "administrator" privileges
		And I am on grade main page        
		And there are keys generated for polls
		When I follow "Generuj klucze"
		Then I wait for a while to see "Brak kluczy do wygenerowania!"
        And I should not see "Wygenerowano klucze RSA"
		And I should be on poll management page
		
	Scenario: Failing to create keys after the grading protocol is started
		Given the grading protocol is "on"
		And I am logged in with "administrator" privileges
		And I am on grade main page        
		When I go to page grade keys generator
		Then I should see "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona"		
