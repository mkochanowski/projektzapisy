Feature: User wants to find some information about Fereol project

  Background:
    Given I go to http://www.ii.uni.wroc.pl/cms
    
  Scenario: Looking for Fereol in search engine
    When I fill in "edit-keys" with "fereol"
    And I press "Szukaj"
    Then I should see "Nie znaleziono pasujących stron"
    And I should not see "fereol"
