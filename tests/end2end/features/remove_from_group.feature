Feature: Student wants to remove himself from a group in order not to learn too much

  Background:
    Given I start new scenario
    And I am logged in
    When I enroll in "Rachunek lambda" in group with id "152"    

  Scenario: Student unenrolls from a group
    When I am on courses page
    And I click on "Rachunek lambda"
    And I press "wypisz" next to "group-id" with value "152"
    And I sleep for 2 seconds
    Then I should see "Zostałeś wypisany z grupy."
    And I should see button "zapisz" next to "group-id" with value "152"
  
