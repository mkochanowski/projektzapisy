Feature: student wants to enroll in all the groups that he pinned on his schedule

  Background:
    Given I start new scenario
    And I am logged in
    And I am on schedule prototype page
  
  @TODO
  Scenario: Schedule prototype lets the student pin two groups
    When I click on "Wprowadzenie do logiki formalnej"
    Then I should see "Zdzisława Jarosz" near "Logika formalna"
    #When I pin the group "Zdzisława Jarosz" near "Logika formalna"
    #Then I should see "odepnij od planu" near "Zdzisława Janosz" on mouseover
    When I click on "Kurs: UNIX - środowisko i narzędzia programowania"
    Then I should see "Alina Leszczyńska" near "Kurs: UNIX"
    #When I pin the group "Alina Leszczyńska" near "Kurs: UNIX"
    #Then I should see "odepnij od planu" near "Alina Leszczyńska" on mouseover

  @TODO
  Scenario: Schedule prototype lets the student enroll in all the pinned groups
    ### No, it doesn't. Is it a bug or a feature?
    #When I press "Zapisz mnie na przypiete przedmioty"
    #Then I should see "Zostałeś zapisany do grupy."
