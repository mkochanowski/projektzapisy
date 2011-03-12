Feature: student wants to enroll in a group that he pinned to his schedule

  Background:
    Given I am logged in
    And I am on schedule prototype page
  
  Scenario: Schedule prototype lets the student pin three groups
    When I click on "Zastosowania wielomianów Czebyszewa"
    Then I should see "Zastosowania wielomianów Czebyszewa: ćwiczenia - Artur Nowakowski16"
    When I pin the group "108"
    Then I should see "Zostałeś przypiety do grupy."

  Scenario: Schedule prototype lets the student enroll in a pinned course
    When I enroll in a pinned group "108"
    Then I should see "Zostałeś zapisany do grupy."
