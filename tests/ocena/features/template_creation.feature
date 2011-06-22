Feature: User with privileges wants to create a template for poll.

    Scenario: First preparations
        Given I start new scenario
        And there are some courses with groups for current semester
        And there are some sections created already
        And the grading protocol is "off"
        
    Scenario: Administrator cannot add the same section twice in a template
		Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Lista szablonów" 
        And I press "Utwórz nowy"    
        And I select "Wybierz sekcję:" as "Ogół zajęć"
        And I press "Dodaj sekcję"
        Then I can not select "Ogół zajęć" from "Wybierz sekcję: "        
        
    Scenario: Administrator creates a template with no course or group assigned
		Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"   
        And I follow "Lista szablonów" 
        And I press "Utwórz nowy"
        And I fill in "Tytuł:" with "Ogół zajęć w instytucie"
        And I select "Wybierz sekcję:" as "Ogół zajęć"
        And I press "Dodaj sekcję"
        And I press "Stwórz szablon"
        Then I should see "Utworzono szablon"
    
    Scenario: Administrator creates a template for every lecture there is
		Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Lista szablonów" 
        And I press "Utwórz nowy"
        And I fill in "Tytuł:" with "Ankieta do wykładu"
        And I select "Przedmiot:" as "Wszystkie przedmioty"
        And I select "Typ zajęć:" as "wykład"        
        And I select "Wybierz sekcję:" as "Wykład"
        And I press "Dodaj sekcję"
        And I select "Wybierz sekcję:" as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz szablon"
        Then I should see "Utworzono szablon"

    Scenario: Employee fails to create a template
        Given I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Lista szablonów" 
        Then I should not see "Utwórz nowy"

    Scenario: Administrator fails to create a template when there is no title
		Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Lista szablonów" 
        And I press "Utwórz nowy"  
        And I select "Wybierz sekcję: " as "Uwagi"
        And I press "Dodaj sekcję"
        And I press "Stwórz szablon"
        Then I should see "To pole jest wymagane"
            
    Scenario: Administrator fails to create a template when there are no sections
		Given I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"    
        And I follow "Lista szablonów" 
        And I press "Utwórz nowy"  
        And I fill in "Tytuł: " with "Ankieta bez treści"
        And I press "Stwórz szablon"
        Then I wait for a while to see "Nie można utworzyć szablonu; szablon jest pusty"     
