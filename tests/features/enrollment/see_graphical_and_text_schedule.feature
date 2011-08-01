Feature: Student wants to see the classes he enrolled in in his schedule

  Scenario: 
    Given I start new scenario
    And I am logged in
    And I enroll in "Bazy danych" in group with id "201"
    And I enroll in "Licencjacki projekt programistyczny" in group with id "174"
    And I enroll in "Rachunek lambda" in group with id "152"

    And I am on schedule page
    Then I should see "Wtorek" within "#enr-schedule-scheduleContainer"
    And I should see "Bazy danych" within "#enr-schedule-scheduleContainer"
    And I should see "LPP" within "#enr-schedule-scheduleContainer"
    And I should see "Rachunek lambda" within "#enr-schedule-scheduleContainer"
    And I should see "Bazy danych" within "#enr-schedule-listByCourse"
    And I should see "Licencjacki projekt programistyczny" within "#enr-schedule-listByCourse"
    And I should see "Rachunek lambda" within "#enr-schedule-listByCourse"
