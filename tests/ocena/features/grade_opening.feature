Feature: Behaviour of the system when trying to open grading

	Background:
        Given I start new scenario      
        And the grading protocol is "off"		
		And I am logged in with "administrator" privileges
		And I am on grade main page

	Scenario: No polls in the system - failure
		When I follow "Otwórz ocenę"	
		Then I should see "Nie można otworzyć oceny; brak ankiet"
		And I should be on grade main page

    Scenario: Not all the polls are in the system - warning
        # Given there are polls generated
        # And there are keys generated for polls
        # And there are subjects without a poll
        # When I follow "Otwórz ocenę"
        # Then I should see a warning "Brak ankiet dla grup:"
        # And I should see "tu wpisujemy nazwę grupy, która będzie dodana w kroku subjects without a poll"
   
    Scenario: Not all the polls are in the system - success
        # Given there are polls generated
        # And there are keys generated for polls
        # And there are subjects without a poll
        # When I follow "Otwórz ocenę"
        # And I press "napis odpowiedni dla otwierania 'mimo wszystko'" in warning window
        # Then I should see "Ocena zajęć otwarta"
        # And I should be on grade main page
        
    Scenario: Not all the polls are in the system - failure        
        # Given there are polls generated
        # And there are keys generated for polls
        # And there are subjects without a poll
        # When I follow "Otwórz ocenę"
        # And I press "napis odpowiedni dla nie otwierania" in warning window
        # Then I should see "Anulowano otwarcie oceny zajęć"
        # And I should be on groups without polls page        
		
	Scenario: Not all the polls have keys generated        
		# Given there are polls generated
		# And there are keys generated for polls
		# And I add new poll
		# When I follow "Otwórz ocenę"		
		# And I should see "Brak kluczy dla niektórych ankiet"
        # And I should see "Generowanie kluczy"
        # And I wait for a while to see "100%"
        # And I click anywhere
        # Then I should see "Ocena zajęć otwarta"
		# And I should be on grade main page
	
	Scenario: Successfully opening grading
		Given there are polls generated
		And there are keys generated for polls
		When I follow "Otwórz ocenę"
		Then I should see "Ocena zajęć otwarta"
        And I should see link "Zamknij ocenę"        
		And I should be on grade main page
