Feature: Student wants to remove himself from a group on fereol-mobile

Background:
    Given I am logged in

Scenario: Student unenrolls from a group
    When I am on subjects page
    And I click on "Algebra"
    And I press "zapisz" next to "group-id" with value "251"
    And I am on the mobile home page
    And I follow "Zapisy"
    # We have some cookies, rawr!
    #And I fill in "Nazwa użytkownika" with "student-test"
    #And I fill in "Hasło" with "aaa"
    #And I press "Zaloguj"
    And I follow "Algebra"
    And I unenroll to group with id "251" on mobile
    Then I should see "Zostałeś wypisany z grupy."
