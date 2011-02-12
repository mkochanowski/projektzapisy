Feature: User with privilages wants to create a section.
    
    Background:
        Given I start new scenario
    
    Scenario: Employee creates a simple section
		Given the grading protocol is "off"
        And I am logged in with "employee" privilages
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"
        And I fill in "Tytuł sekcji" with "Sekcja przykładowego pracownika"
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Jak podobał Ci się mój przedmiot?"
        And I click "Zapisz"
        Then I should see "Sekcja dodana"
    
    Scenario: Administrator creates a simple section
		Given the grading protocol is "off"
        And I am logged in with "administrator" privilages
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"
        And I fill in "Tytuł sekcji" with "Sekcja administratora"
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Jak podobała Ci się moja praca?"
        And I click "Zapisz"
        Then I should see "Sekcja dodana"    
    
    Scenario: Administrator creates a more complex section with many different types of questions
		Given the grading protocol is "off"
        And I am logged in with "administrator" privilages
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"
        And I fill in "Tytuł sekcji" with "Sekcja administratora - złożona"
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Jak podobała Ci oferta w tym semestrze?"
        And I select "Typ pytania" as "Pytanie otwarte"
        And I click "Gotowe"
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Czy była dość bogata?"
        And I select "Typ pytania" as "Pytanie jednokrotnego wyboru"
        And I fill in "odpowiedź" with "tak"
        And I click "Gotowe"        
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "trudno powiedzieć"
        And I click "Gotowe"        
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "nie"
        And I click "Gotowe" 
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Czego było za mało?"
        And I select "Typ pytania" as "Pytanie wielokrotnego wyboru"
        And I fill in "odpowiedź" with "Algorytmów"
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "Sieci"
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "Kryptografii"
        And I click "Gotowe"
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Czego było za dużo?"
        And I select "Typ pytania" as "Pytanie wielokrotnego wyboru"
        And I fill in "odpowiedź" with "Algorytmów"
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "Sieci"
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "Kryptografii"
        And I check "Odpowiedź inne"
        And I click "Gotowe"
        And I click "Zapisz"        
        Then I should see "Sekcja dodana"    

            
    Scenario: Administrator creates a section with opening question
		Given the grading protocol is "off"
        And I am logged in with "administrator" privilages
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"
        And I fill in "Tytuł sekcji" with "Sekcja administratora - pytanie otwierające"
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Czy podobała Ci oferta w tym semestrze?"
        And I select "Typ pytania" as "Pytanie wiodące"
        And I fill in "odpowiedź" with "tak"
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "trudno powiedzieć"
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "nie"
        And I check "Ukryj sekcję"        
        And I click "Gotowe"
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Czy była dość bogata?"
        And I select "Typ pytania" as "Pytanie jednokrotnego wyboru"
        And I fill in "odpowiedź" with "tak"
        And I click "Gotowe"        
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "trudno powiedzieć"
        And I click "Gotowe"        
        And I click "Dodaj odpowiedź"
        And I fill in "odpowiedź" with "nie"
        And I click "Dodaj odpowiedź"                
        And I click "Gotowe"        
        And I click "Zapisz"        
        Then I should see "Sekcja dodana" 
    
    Scenario: Student enters the section creation page
		Given the grading protocol is "off"
        And I am logged in with "student" privilages
        And I am on grade main page    
        When I go to grade/poll/managment/section_create
        Then I should see "Zaloguj"

    
    Scenario: While grading protocol is active, the administrator tries to create a section
		Given the grading protocol is "on"
        And I am logged in with "administrator" privilages
        And I am on grade main page    
        When I go to grade/poll/managment/section_create
        Then I should see "Ocena zajęć jest aktywna, nie można dodawać sekcji"
    
    Scenario: Administrator tries to create section with no questions
		Given the grading protocol is "off"
        And I am logged in with "administrator" privilages
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"  
        And I fill in "Tytuł sekcji" with "Sekcja administratora"
        And I click "Zapisz"        
        Then I should see "Błąd: sekcja nie zawiera pytań"
            
    Scenario: Administrator tries to create section without a title
		Given the grading protocol is "off"
        And I am logged in with "administrator" privilages
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"      
        And I fill in "Tytuł sekcji" with ""
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Jak podobała Ci się moja praca?"
        And I click "Zapisz"
        Then I should see "Błąd: brak tytułu sekcji"
    
    Scenario: Administrator tries to create section with a default title
		Given the grading protocol is "off"
        And I am logged in with "administrator" privilages
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"      
        And I click "Dodaj pytanie"
        And I fill in "Podaj treść pytania" with "Jak podobała Ci się moja praca?"
        And I click "Zapisz"        
        Then I should see "Błąd: podaj poprawny tytuł sekcji"
    
    Scenario outline: Administrator tries to add a question without a question text
		Given the grading protocol is "off"
        And I am logged in with "administrator" privilages
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"    
        And I fill in "Tytuł sekcji" with "Sekcja administratora"         
        And I click "Dodaj pytanie"
        And I select "Typ pytania" as <typ_pytania>
        And I click "Zapisz"
        Then I should see "Błąd: brak tekstu w pytaniu
        
    Examples:
        | typ_pytania |
        | "Otwarte" |
        | "Jednokrotnego wyboru" |
        | "Wielokrotnego wyboru" |
        | "Pytanie wiodące" |
    
    Scenario outline: Administrator tries to add a choice question with no choices
		Given the grading protocol is "off"
        And I am logged in with "administrator" privilages
        And I am on grade main page
        When I follow "Zarządzaj ankietami"
        And I follow "Tworzenie sekcji"      
        And I fill in "Tytuł sekcji" with "Sekcja administratora"
        And I click "Dodaj pytanie"
        And I select "Typ pytania" as <typ_pytania>
        And I fill in "Podaj treść pytania" with "Treść pytania"
        And I click "Zapisz"
        Then I should see "Błąd: brak tekstu w pytaniu

    Examples:
        | typ_pytania |
        | "Jednokrotnego wyboru" |
        | "Wielokrotnego wyboru" |
        | "Pytanie wiodące" |
