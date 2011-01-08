Feature: User wants to sign in in order to use functions which aren't publicly available

  Background:
    Given I am on the home page
    
  Scenario: Successful signing in with student credentials 
    When I follow "System zapisów"
    And I follow "Zaloguj"
    And I fill in "Nazwa użytkownika" with "student-test"
    And I fill in "Hasło" with "aaa"
    And I press "Zaloguj"
    Then I should be on my profile page

  Scenario: Unsuccessful signing in with invalid user name
    When I follow "System zapisów"
    And I follow "Zaloguj"
    And I fill in "Nazwa użytkownika" with "student-test-invalid"
    And I fill in "Hasło" with "aaa"
    And I press "Zaloguj"
    Then I should see "Podany identyfikator i hasło się nie zgadzają. Spróbuj ponownie"
    
  Scenario: Signing in with invalid password
    When I follow "System zapisów"
    And I follow "Zaloguj"
    And I fill in "Nazwa użytkownika" with "student-test"
    And I fill in "Hasło" with "bbb"
    And I press "Zaloguj"
    Then I should see "Podany identyfikator i hasło się nie zgadzają. Spróbuj ponownie"
