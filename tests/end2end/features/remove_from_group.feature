Feature: Student wants to remove himself from a group in order not to learn too much

  Background:
    Given I am logged in
    
  Scenario: Student enrolls in a group
    When I enroll in "Rachunek lambda" in group with id "185"

  Scenario: Student unenrolls from a group
    When I am on subjects page
    And I click on "Rachunek lambda"
    And I press "wypisz" next to "group-id" with value "185"
    And I sleep for 2 seconds
    Then I should see "Zostałeś wypisany z grupy."
    Then I should see button "zapisz" next to "group-id" with value "185"
  
