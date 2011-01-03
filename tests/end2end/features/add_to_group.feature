Feature: Student wants to add himself to group in order to learn something

  Background:
    When I am on the home page
    And I follow "System zapisów"
    And I follow "Zaloguj"
    And I fill in "Nazwa użytkownika" with "student-test"
    And I fill in "Hasło" with "aaa"
    And I press "Zaloguj"
    
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
    And I click on link which points to "/records/199/assign"
    
