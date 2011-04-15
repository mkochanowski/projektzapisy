Feature: Student wants to add himself to group in order to learn something

  Background:
    Given I start new scenario
    And I am logged in
    
  Scenario: Subjects page is accessible
    When I follow "System zapisów"
    And I follow "Przedmioty"
    Then I should be on subjects page
    
  Scenario: Subject page is accessible
    When I am on subjects page
    And I click on "Bazy danych"
    Then I should see "Bazy danych" within "#enr-subject-view"
    
  Scenario: Successful adding to group
    When I am on subjects page
    And I click on "Bazy danych"
    And I press "zapisz" next to "group-id" with value "201"
    And I sleep for 2 seconds
    Then I should see button "wypisz" next to "group-id" with value "201"
