Feature: student wants to enroll in all the groups that he pinned on his schedule

  Background:
    Given I am logged in
    And I am on schedule prototype page
  
  Scenario: Schedule prototype lets the student pin three groups
    When I click on "Wprowadzenie do logiki formalnej"
    Then I should see "Wprowadzenie do logiki formalnej: ćwiczenia - Artur Nowakowski3"
    # Uncomment & correct when prototype is fully functional
    # When I pin the group "110"
    # Then I should see "Zostałeś przypiety do grupy."
    # When I click on "Kurs: UNIX - środowisko i narzędzia programowania"
    # Then I should see "Kurs: UNIX - środowisko i narzędzia programowania: pracownia - Artur"
    # When I pin the group "178"
    # Then I should see "Zostałeś przypiety do grupy."
    # When I pin the group "179"
    # Then I should see "Zostałeś przypiety do grupy."

  Scenario: Schedule prototype lets the student enroll in all the pinned groups
    # When I press "Zapisz mnie na przypiete przedmioty"
    # Then I should see "Zostałeś zapisany do grupy."
