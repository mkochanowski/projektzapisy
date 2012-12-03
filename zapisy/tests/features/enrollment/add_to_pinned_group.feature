Feature: student wants to enroll in a group that he pinned to his schedule

  @TODO
  Scenario: Schedule prototype lets the student pin two groups
     Given I start new scenario for "enrollment"
     And I am logged in
     And I am on schedule prototype page
     When I click on "Zastosowania wielomianów Czebyszewa"    
     Then I should see "Zdzisława Jarosz" near "Zast. w. Czebyszewa"
     #When I pin the group "Zdzisława Jarosz" near "Zast. w. Czebyszewa"
     #Then I should see "odepnij od planu" near "Zdzisława Janosz" on mouseover

  @TODO
  Scenario: Schedule prototype lets the student enroll in a pinned course
    #When I enroll in a pinned group "Zdzisława Jarosz"
    #Then I should see "wypisz z grupy" near "Zdzisława Janosz" on mouseover
