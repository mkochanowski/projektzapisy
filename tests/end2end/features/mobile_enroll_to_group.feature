Feature:  Student wants to add himself to group in order to learn something on fereol-mobile

Background:
     Given I start new scenario
     And I am on the mobile home page
     And I follow "Zapisy"
     And I fill in "Nazwa użytkownika" with "student-test"
     And I fill in "Hasło" with "aaa"
     And I press "Zaloguj"

Scenario: Successful adding to group
    When I follow "Wszystkie przedmioty"
    When I follow "Bazy danych"
    And I enroll to group with id "201" on mobile
    Then I should see "Zostałeś zapisany do grupy."
    When I follow "przejdź do pełnej wersji"
    And I follow "System zapisów"
    And I follow "Przedmioty"
    And I follow "Bazy danych"
    Then I should see button "wypisz" next to "group-id" with value "201"
