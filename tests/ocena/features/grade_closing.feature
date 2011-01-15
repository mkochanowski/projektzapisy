Feature: Behaviour of the system after closing grading /przenieść do odpowiednich miejsc/

	Background:
		Given the grading protocol is "off"
		
	
	Scenario: Student tries to present a ticket		
		When I go to /grade/poll/tickets_enter
		Then I should see "Ocena zajęć jest w tej chwili zamknięta; nie można przestawić biletu na ankietę"
	
	Scenario: Student tries to edit a poll				
		When I go to /grade/poll/edit/1
		Then I should see "Ocena zajęć jest w tej chwili zamknięta"
		
	Scenario: Administrator can see the grading results
		Given I am logged in with "administrator" privileges
		And there are some polls filled for current semester
		When I follow "Wyniki oceny"
		And I choose current semester
		Then I should see all the polls filled for current semester
