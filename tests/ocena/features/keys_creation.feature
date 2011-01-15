Feature: Creating keys for polls in the grading protocol

	Background:
		Given I am logged in with "administrator" priviliges
		And I am on grade main page
	
	
	Scenario: Successfully creating keys for all the polls
		Given the grading protocol is "off"
		And there are some polls generated
		When I click "Generuj klucze"		
		And I wait for "5" seconds
		Then I should see "Wygenerowano klucze RSA"
		And I should be on pool management page
	
	Scenario: Successfully creating additional keys for added polls
		Given the grading protocol is "off"
		And there are polls generated
		And there are keys generated for polls
		When I add new poll
		And I follow "Generuj klucze"
		And I wait for "2" seconds
		Then I should see "Wygenerowano klucze RSA"
		And I should be on pool management page
	
	Scenario: Failing to create keys - all the polls already have them
		Given the grading protocol is "off"
		And there are polls generated
		And there are keys generated for polls
		When I follow "Generuj klucze"
		And I wait for "2" seconds
		Then I should see "Brak nowych ankiet"
		And I should be on pool management page
		
	Scenario: Failing to create keys after the grading protocol is started
		Given the grading protocol is "on"
		When I go to page "/grade/ticket/keys_generate"
		Then I should see "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona"		
