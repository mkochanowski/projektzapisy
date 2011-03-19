Feature: student wants to pin a group to his schedule prototype

  Background:
    Given I am logged in
    And I am on schedule prototype page
  
  Scenario: Schedule prototype shows the groups of clicked course
    When I click on "Wprowadzenie do logiki formalnej"
    Then I should see "Wprowadzenie do logiki formalnej: wykład - Artur Nowakowski16"
  
  Scenario: Schedule prototype lets the student pin a group
    When I click on "Wprowadzenie do logiki formalnej"
    Then I should see "Wprowadzenie do logiki formalnej: wykład - Artur Nowakowski16"
    When I pin the group "109"
    Then I should see "Zostałeś przypiety do grupy."
