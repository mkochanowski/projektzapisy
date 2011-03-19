Feature: Student wants to see the classes he enrolled in in his schedule

  Background:
    Given I am logged in
    
  Scenario: Schedule page shows the courses that we enroll in
    When I enroll in "Bazy danych" in group with id "188"
    And I enroll in "Licencjacki projekt programistyczny" in group with id "164"
    And I enroll in "Rachunek lambda" in group with id "141"

    And I am on schedule page
    Then I should see "Wtorek" within "#schedule-wrapper"
    And I should see "Bazy danych" within "#schedule-wrapper"
    And I should see "Licencjacki projekt programistyczny" within "#schedule-wrapper"
    And I should see "Rachunek lambda" within "#schedule-wrapper"
    And I should see "Bazy danych" within ".schedule-table-simple"
    And I should see "Licencjacki projekt programistyczny" within ".schedule-table-simple"
    And I should see "Rachunek lambda" within ".schedule-table-simple"