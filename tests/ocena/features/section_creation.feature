Feature: User with privileges wants to create a section.
    
    Background:
        Given I start new scenario
    
    Scenario: Employee creates a simple section
		Given the grading protocol is "off"
        And I am logged in with "employee" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"
        And I fill in "section-title" with "Sekcja przykładowego pracownika"
        And I press "Dodaj pytanie" 
        And I fill in "poll[question][1][title]" with "Jak podobał Ci się mój przedmiot?"
        And I press "Zapisz" 
        Then I should see "Sekcja dodana"
    
    Scenario: Administrator creates a simple section
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"
        And I fill in "section-title" with "Sekcja administratora"
        And I press "Dodaj pytanie" 
        And I fill in "poll[question][1][title]" with "Jak podobała Ci się moja praca?"
        And I press "Zapisz" 
        Then I should see "Sekcja dodana"    
    
    Scenario: Administrator creates a more complex section with many different types of questions
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"
        And I fill in "section-title" with "Sekcja administratora - złożona"
        And I press "Dodaj pytanie" 
        And I fill in "poll[question][1][title]" with "Jak podobała Ci oferta w tym semestrze?"
        And I select "poll[question][1][type]" as "Otwarte"
        And I press visible "Gotowe"
        And I press "Dodaj pytanie" 
        And I fill in "poll[question][2][title]" with "Czy była dość bogata?"
        And I select "poll[question][2][type]" as "Jednokrotnego wyboru"
        And I fill in "poll[question][2][answers][1]" with "tak"
        And I press visible "Dodaj odpowiedź" 
        And I fill in "poll[question][2][answers][2]" with "trudno powiedzieć"
        And I press visible "Dodaj odpowiedź" 
        And I fill in "poll[question][2][answers][3]" with "nie"
        And I press visible "Gotowe"
        And I press "Dodaj pytanie" 
        And I fill in "poll[question][3][title]" with "Czego było za mało?"
        And I select "poll[question][3][type]" as "Wielokrotnego wyboru"
        And I fill in "poll[question][3][answers][1]" with "Algorytmów"
        And I press visible "Dodaj odpowiedź"
        And I fill in "poll[question][3][answers][2]" with "Sieci"
        And I press visible "Dodaj odpowiedź" 
        And I fill in "poll[question][3][answers][3]" with "Kryptografii"
        And I press visible "Gotowe"
        And I press "Dodaj pytanie" 
        And I fill in "poll[question][4][title]" with "Czego było za dużo?"
        And I select "poll[question][4][type]" as "Wielokrotnego wyboru"
        And I fill in "poll[question][4][answers][1]" with "Algorytmów"
        And I press visible "Dodaj odpowiedź" 
        And I fill in "poll[question][4][answers][2]" with "Sieci"
        And I press visible "Dodaj odpowiedź" 
        And I fill in "poll[question][4][answers][3]" with "Kryptografii"
        And I check "poll[question][4][hasOther]"
        And I press visible "Gotowe"
        And I press "Zapisz"    
        Then I should see "Sekcja dodana"    
            
    Scenario: Administrator creates a section with opening question
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"
        And I fill in "section-title" with "Sekcja administratora - pytanie wiodące"
        And I check "poll[leading]"
        And I fill in "poll[question][0][title]" with "Czy podobała Ci oferta w tym semestrze?"
        And I fill in "poll[question][0][answers][1]" with "tak"
        And I press visible "Dodaj odpowiedź" 
        And I fill in "poll[question][0][answers][2]" with "trudno powiedzieć"
        And I press visible "Dodaj odpowiedź" 
        And I fill in "poll[question][0][answers][3]" with "nie"
        And I check "poll[question][0][hideOn][]" with value "3"
        And I press visible "Gotowe"        
        And I press "Dodaj pytanie" 
        And I fill in "poll[question][1][title]" with "Czy była dość bogata?"
        And I select "poll[question][1][type]" as "Jednokrotnego wyboru"
        And I fill in "poll[question][1][answers][1]" with "tak"   
        And I press visible "Dodaj odpowiedź" 
        And I fill in "poll[question][1][answers][2]" with "trudno powiedzieć"
        And I press visible "Dodaj odpowiedź" 
        And I fill in "poll[question][1][answers][3]" with "nie"
        And I press visible "Gotowe"         
        And I press "Zapisz"         
        Then I should see "Sekcja dodana" 
    
    Scenario: Student enters the section creation page
		Given the grading protocol is "off"
        And I am logged in with "student" privileges
        And I am on grade main page    
        When I go to /grade/poll/managment/section_create
        Then I should see "Zaloguj"

    
    Scenario: While grading protocol is active, the administrator tries to create a section
		Given the grading protocol is "on"
        And I am logged in with "administrator" privileges
        And I am on grade main page    
        When I go to /grade/poll/managment/section_create
        Then I should see "Ocena zajęć jest otwarta; operacja nie jest w tej chwili dozwolona"
    
    Scenario: Administrator tries to create section with no questions
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"  
        And I fill in "section-title" with "Sekcja administratora"
        And I press "Zapisz"         
        Then I should see "Nie można utworzyć sekcji:"
	And I should see "Sekcja nie zawiera pytań"
            
    Scenario: Administrator tries to create section without a title
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"      
        And I press "Dodaj pytanie" 
        And I fill in "poll[question][1][title]" with "Jak podobała Ci się moja praca?"
        And I press "Zapisz" 
        Then I should see "Nie można utworzyć sekcji:"
	And I should see "Niepoprawny tytuł sekcji"
    
    Scenario Outline: Administrator tries to add a question without a question text
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"    
        And I fill in "section-title" with "Sekcja administratora"         
        And I press "Dodaj pytanie" 
        And I select "poll[question][1][type]" as <typ_pytania>
        And I press "Zapisz" 
        Then I should see "Nie można utworzyć sekcji:"
	And I should see "Pytanie 1:" 
	And I should see "brak tekstu"
        
    Examples:
        | typ_pytania |
        | "Otwarte" |
        | "Jednokrotnego wyboru" |
        | "Wielokrotnego wyboru" |
    
    Scenario Outline: Administrator tries to add a choice question with no choices
		Given the grading protocol is "off"
        And I am logged in with "administrator" privileges
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"      
        And I fill in "section-title" with "Sekcja administratora"
        And I press "Dodaj pytanie" 
        And I select "poll[question][1][type]" as <typ_pytania>
        And I fill in "poll[question][1][title]" with "Treść pytania"
        And I press "Zapisz" 
        Then I should see "Nie można utworzyć sekcji:"
	And I should see "Pytanie 1:"
	And I should see "brak opcji"

    Examples:
        | typ_pytania |
        | "Jednokrotnego wyboru" |
        | "Wielokrotnego wyboru" |
