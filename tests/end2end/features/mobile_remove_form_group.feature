Feature: Student wants to remove himself from a group on fereol-mobile

Background:
    Given I am logged in

Scenario: Student unenrolls from a group
    When I am on subjects page
    And I click on "Algebra"
    And I click on link which points to "/records/196/assign"
    And I am on the mobile home page
    And I follow "Zapisy"
    And I fill in "Nazwa użytkownika" with "student-test"
    And I fill in "Hasło" with "aaa"
    And I press "Zaloguj"
    And I follow "Algebra"
    And I unenroll to group with id "196" on mobile
    Then I should see "Zostałeś wypisany z grupy."
