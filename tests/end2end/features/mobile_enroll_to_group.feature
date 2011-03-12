Feature:  Student wants to add himself to group in order to learn something on fereol-mobile

Background:
     Given I am on the mobile home page
     And I follow "Zapisy"
     And I fill in "Nazwa użytkownika" with "student-test"
     And I fill in "Hasło" with "aaa"
     And I press "Zaloguj"

Scenario: Successful adding to group
     When I follow "Inne przedmioty"
     And I follow "Bazy danych"
     And I enroll to group with id "188" on mobile
     #And I am in the home page
     Then I should see "Zostałeś zapisany do grupy."
     And I follow "przejdź do pełnej wersji"
     And I follow "System zapisów"
     And I follow "Przedmioty"
     And I follow "Bazy danych"
     Then I should see link "/records/188/resign"