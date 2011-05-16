Feature: Student wants to remove himself from a group on fereol-mobile

Background:
    Given I start new scenario
    And I am logged in

Scenario: Student unenrolls from a group
    When I am on courses page
    And I click on "Bazy danych"
    And I press "zapisz" next to "group-id" with value "201"
    And I am on the mobile home page
    And I follow "Zapisy"
    And I fill in "Nazwa użytkownika" with "student-test"
    And I fill in "Hasło" with "aaa"
    And I press "Zaloguj"
    And I follow "Bazy danych"
    And I unenroll to group with id "201" on mobile
    Then I should see "Zostałeś wypisany z grupy."
