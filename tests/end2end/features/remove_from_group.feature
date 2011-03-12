Feature: Student wants to remove himself from a group in order not to learn too much

  Background:
    Given I am logged in
    
  Scenario: Student enrolls in a group
    When I enroll in "Rachunek lambda" in group with id "140"

  Scenario: Student unenrolls from a group
    When I am on subjects page
    And I click on "Rachunek lambda"
    And I click on link which points to "/records/140/resign"
    And I sleep for 2 seconds
    Then I should see "Zostałeś wypisany z grupy."
    And I should see link which points to "/records/140/assign"
  