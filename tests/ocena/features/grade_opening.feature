Feature: Behaviour of the system when trying to open grading

    Background:
      Given I start new scenario      
      And the grading protocol is "off"     
      And I am logged in with "administrator" privileges
      And I am on grade main page

    Scenario: No polls in the system - failure
      When I follow "Otwórz ocenę"  
      Then I should see "Nie można otworzyć oceny; brak ankiet"
      And I should be on grade main page

    @TODO
    Scenario: Not all the polls are in the system - warning
      Given there are polls generated
      And there are keys generated for polls        
      And there are courses without a poll
      When I follow "Otwórz ocenę"
      #Then I should see a warning "Brak ankiet dla grup:"
      #And I should see a warning "Nowy przedmiot testowy"

    @TODO   
    Scenario: Not all the polls are in the system - success
      Given there are polls generated
      And there are keys generated for polls
      And there are courses without a poll
      When I follow "Otwórz ocenę"
      #And I press "Otwórz ocenę mimo to" in warning window
      #Then I should see "Ocena zajęć otwarta"
      #And I should be on grade main page
       
    @TODO 
    Scenario: Not all the polls are in the system - failure        
      Given there are polls generated
      And there are keys generated for polls
      And there are courses without a poll
      When I follow "Otwórz ocenę"
      #And I press "Cofnij" in warning window
      #Then I should see "Anulowano otwarcie oceny zajęć"
      #And I should be on groups without polls page        
        
    Scenario: Successfully opening grading
      Given there are polls generated
      And there are keys generated for polls
      When I follow "Otwórz ocenę"
      Then I should see "Ocena zajęć otwarta"
      And I should see link "Zamknij ocenę"        
      And I should be on grade main page
