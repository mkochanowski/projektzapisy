Feature: User wants to see a list of pinned and enrolled lecture in mobile-fereol

Background:
    Given I start new scenario
    And I am on the home page
    And I am logged in

Scenario: See a pin lecture in pin lecture list in fereol-mobile
    #Uncomment when prototype starts to work!
    #Given I am on schedule prototype page
    #And I click on "Rachunek lambda"
    #And I pin the group "141"
    #When I follow "wyloguj"
    #And I am on the mobile home page
    #And I follow "Zapisy"
    #And I fill in "Nazwa użytkownika" with "student-test"
    #And I fill in "Hasło" with "aaa"
    #And I press "Zaloguj"
    #Then I should see "Rachunek lambda"

Scenario: See a enrolled lecture in enrolled lecture list in fereol-mobile
    Given I enroll in "Programowanie" in group with id "169"
    When I follow "wyloguj"
    And I am on the mobile home page
    And I follow "Zapisy"
    And I fill in "Nazwa użytkownika" with "student-test"
    And I fill in "Hasło" with "aaa"
    And I press "Zaloguj"
    Then I should see "Programowanie"
