Feature: Student wants to add himself to group in order to learn something

  Background:
    Given I am logged in
    
  Scenario: Subjects page is accessible
    When I follow "System zapisów"
    And I follow "Przedmioty"
    Then I should be on subjects page
    
  Scenario: Subject page is accessible
    When I am on subjects page
    And I click on "Algebra"
    Then I should see "Algebra" within "#subject-details"
    
  Scenario: Successful adding to group
    When I am on subjects page
    And I click on "Algebra"
    And I click on link which points to "/records/196/assign"
    And I sleep for 2 seconds
    Then I should see "wypisz"
    And I should see link which points to "/records/196/resign"