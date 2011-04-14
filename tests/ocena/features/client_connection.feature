Feature: User downloads tickets using supplied external client.

    Background:
        Given I start new scenario
        And there are polls generated 
        And there are keys generated for polls
        And the grading protocol is "on"
        And I am signed for groups with polls
		And I am logged in with "student" privileges	
        
    Scenario: Non downloaded tickets should be downloadable
#        Given I am on grade main page
#        And I follow "Pobierz bilety"
#        When I run client with "no_tickets_downloaded"
#        And I press "Pobierz bilety"
#        Then I wait for a while to see "Pomyślnie wygenerowano bilety"
#        And I should not see "Bilet już pobrano"
        
    Scenario: Downloaded ticket should not be downloadable
#        Given I am on grade main page
#        And I follow "Pobierz bilety"
#        When I run client with "ticket_downloaded"
#        And I press "Pobierz bilety"
#        Then I wait for a while to see "Pomyślnie wygenerowano bilety"
		# tu musze wylapac ta ankiete na ktora sciagnalem juz bilet!!!
#        And I should see "Bilet już pobrano"
        
    Scenario: Part of grouping downloaded by client grouping selected in fereol
 #       Given I am on grade main page
 #       And I follow "Pobierz bilety"
 #       When I run client with "part_of_grouping_downloaded"
 #       And I press "Pobierz bilety"
 #       Then I wait for a while to see "Pomyślnie wygenerowano bilety"
		# tu musze wylapac ta ankiete na ktora sciagnalem juz bilet!!!
 #       And I should see "Bilet już pobrano"
        # a tu byc moze sprawdzic ze te bilety nie sa powiazane...
        
    Scenario: Tickets downloaded in fereol are not downloadable
 #       Given I am on grade main page
 #       And I follow "Pobierz bilety"
 #       And I press "Pobierz bilety"
 #       When I run client with "ticket_downloaded"
 #       # tutaj ze nie ma pliku z biletami
        
    Scenario: Downloaded tickets should enable poll filling
  #      Given I am on grade main page
  #      And I follow "Oceń zajęcia"
        # tutaj podanie biletow z pliku [albo przepisanie z tekstowego, albo upload jak sie uda]
  #      And I press "Wyślij" 
  #      Then I should be on polls filling page
  #      Then I should not see "Nie udało się zweryfikować podpisu pod biletem."
        
