Feature: student wants to enroll in a group that he pinned to his schedule

  Background:
    Given I start new scenario
    And I am logged in
    And I am on schedule prototype page
  
  Scenario: Schedule prototype lets the student pin three groups
    When I click on "Zastosowania wielomianów Czebyszewa"
    # Uncomment & correct when prototype is fully functional
    # Then I should see "Zast. w. Czebyszewa: ćwiczenia - Artur Nowakowski19"
    # When I pin the group "142"
    # Then I should see "Zostałeś przypiety do grupy."

  Scenario: Schedule prototype lets the student enroll in a pinned course
    # Uncomment & correct when prototype is fully functional
    # When I enroll in a pinned group "142"
    # Then I should see "Zostałeś zapisany do grupy."
