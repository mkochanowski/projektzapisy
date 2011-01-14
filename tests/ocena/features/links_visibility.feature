Feature: Which links are visibile to which users, depending on the state of the grading protocol

	Background:
		Given I am on grade main page	
		

	Scenario: Anonymous user with grade protocol on
		# Given the grading protocol is "on"
		Then I should see "Oceń zajęcia"
	
	
	Scenario: Student user with grade protocol on	
		Given I am logged in with "student" privileges
		# And the grading protocol is "on"
		Then I should see "Pobierz bilety"
		And I should see "Oceń zajęcia"
		And I should see "Wyniki oceny"
		
	Scenario: Student user with grade protocol off	
		Given I am logged in with "student" privileges
		# And the grading protocol is off
		Then I should see "Wyniki oceny"	


	Scenario: Employee user with grade protocol on	
		Given I am logged in with "employee" privileges
		# And the grading protocol is "on"
		Then I should see "Wyniki oceny"

	Scenario: Employee user with grade protocol off
		Given I am logged in with "employee" privileges
		# And the grading protocol is "off"
		Then I should see "Zarządzaj ankietami"
		And I should see "Wyniki oceny"

		
	Scenario: Administrator user with grade protocol on
		Given I am logged in with "administrator" privileges
		# And the grading protocol is "on"
		Then I should see "Zakończ ocenę"
		And I should see "Wyniki oceny"
	
	Scenario: Administrator user with grade protocol off
		Given I am logged in with "administrator" privileges
		# And the grading protocol is "off"
		Then I should see "Zarządzaj ankietami"
		And I should see "Generuj klucze"
		And I should see "Otwórz ocenę"
		And I should see "Wyniki oceny"
