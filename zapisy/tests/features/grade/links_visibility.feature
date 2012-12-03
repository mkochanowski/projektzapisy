Feature: Which links are visibile to which users, depending on the state of the grading protocol

  Scenario: Anonymous user with grade protocol off
    Given I start new scenario for "grade"  
    And the grading protocol is "off"
    And I am on grade main page
    Then I should see link "Aktualności"
    And I should not see link "Oceń zajęcia"
    And I should not see link "Pobierz bilety"      
    And I should not see link "Zarządzaj ankietami"
    And I should not see link "Zamknij ocenę"
    And I should not see link "Otwórz ocenę"
    And I should not see link "Wyniki oceny"

  Scenario: Student user with grade protocol off    
    Given I am logged in with "student" privileges      
    And I am on grade main page     
    Then I should see link "Aktualności"
    And I should not see link "Oceń zajęcia"
    And I should not see link "Pobierz bilety"      
    And I should not see link "Zarządzaj ankietami"
    And I should not see link "Zamknij ocenę"
    And I should not see link "Otwórz ocenę"
    And I should see link "Wyniki oceny"

  Scenario: Employee user with grade protocol off
    Given I am logged in with "employee" privileges     
    And I am on grade main page   
    Then I should see link "Aktualności"
    And I should not see link "Oceń zajęcia"
    And I should not see link "Pobierz bilety"      
    And I should see link "Zarządzaj ankietami"
    And I should not see link "Zamknij ocenę"
    And I should not see link "Otwórz ocenę"
    And I should see link "Wyniki oceny"
        
  Scenario: Administrator user with grade protocol off
    Given I am logged in with "administrator" privileges        
    And I am on grade main page   
    Then I should see link "Aktualności"
    And I should not see link "Oceń zajęcia"
    And I should not see link "Pobierz bilety"      
    And I should see link "Zarządzaj ankietami"
    And I should not see link "Zamknij ocenę"
    And I should see link "Otwórz ocenę"
    And I should see link "Wyniki oceny"        

  Scenario: Anonymous user with grade protocol on
    Given I start new scenario for "grade"      
    And the grading protocol is "on"
    And I am on grade main page
    Then I should see link "Aktualności" 
    And I should see link "Oceń zajęcia"
    And I should not see link "Pobierz bilety"      
    And I should not see link "Zarządzaj ankietami"
    And I should not see link "Zamknij ocenę"
    And I should not see link "Otwórz ocenę"
    And I should not see link "Wyniki oceny"

  Scenario: Student user with grade protocol on 
    Given I am logged in with "student" privileges      
    And I am on grade main page 
    Then I should see link "Aktualności"
    And I should see link "Oceń zajęcia"
    And I should see link "Pobierz bilety"      
    And I should not see link "Zarządzaj ankietami"
    And I should not see link "Zamknij ocenę"
    And I should not see link "Otwórz ocenę"
    And I should see link "Wyniki oceny"
        
  Scenario: Employee user with grade protocol on    
    Given I am logged in with "employee" privileges     
    And I am on grade main page        
    Then I should see link "Aktualności"
    And I should not see link "Oceń zajęcia"
    And I should not see link "Pobierz bilety"      
    And I should not see link "Zarządzaj ankietami"
    And I should not see link "Zamknij ocenę"
    And I should not see link "Otwórz ocenę"
    And I should see link "Wyniki oceny"

  Scenario: Administrator user with grade protocol on
    Given I am logged in with "administrator" privileges        
    And I am on grade main page
    Then I should see link "Aktualności"
    And I should not see link "Oceń zajęcia"
    And I should not see link "Pobierz bilety"      
    And I should not see link "Zarządzaj ankietami"
    And I should see link "Zamknij ocenę"
    And I should not see link "Otwórz ocenę"
    And I should see link "Wyniki oceny"
    
