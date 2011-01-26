Feature: Anonymous user wants to present tickets for polls in order to anonymously fill the polls

    Background:
        And I start new scenario
        And the grading protocol is "on"
        And there are polls generated
        And there are keys generated for polls
        Given I am on grade main page
        
    Scenario Outline: First entrance of all the tickets
        When I follow "Oceń zajęcia"
        And I fill in "Podaj wygenerowane bilety:" with <ticket>
        And I press "Wyślij" 
        Then I should be on polls filling page
        Then I should not see "Nie udało się zweryfikować podpisu pod biletem."
        
        Examples:
            | ticket  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
            | "[Ankieta 2]Ankieta ogólna  typ studiów: licencjackie  id: 2  11304577320893268228391420576688236555476517901921754212130727677604240925772204231973812110326287676033501333114085724038333343931171186288596112485688378  31734325192917143944466127908890793821179582586626629958226855693777598793367785088947241788110381050955523196190991176574965873455664272162371790386537647647432744486649188767324069823118147246454621182364395747288277369384288450930143315750566738592059298898717724782661738514467974355581398302460061546390  ---------------------------------- " |
        
    
    Scenario Outline: Entrance of the tickets in order to edit the polls
        Given I have previously saved some data in polls using <ticket>
        When I follow "Oceń zajęcia"
        And I fill in "Podaj wygenerowane bilety:" with <ticket>
        And I press "Wyślij"
        Then I should not see "Nie udało się zweryfikować podpisu pod biletem."
        
        Examples:
            | ticket                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
            | "[Ankieta 2]Ankieta ogólna  typ studiów: licencjackie  id: 2  11304577320893268228391420576688236555476517901921754212130727677604240925772204231973812110326287676033501333114085724038333343931171186288596112485688378  31734325192917143944466127908890793821179582586626629958226855693777598793367785088947241788110381050955523196190991176574965873455664272162371790386537647647432744486649188767324069823118147246454621182364395747288277369384288450930143315750566738592059298898717724782661738514467974355581398302460061546390  ---------------------------------- " |
            
            
    Scenario Outline: Failure - one of the tickets is not properly signed
        When I follow "Oceń zajęcia"
        And I fill in "Podaj wygenerowane bilety:" with <good_bad_ticket>
        And I press "Wyślij"
        Then I should see "Nie udało się zweryfikować podpisu pod biletem."        
        
        Examples:
            | good_bad_ticket                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 
            | "[Ankieta 2]Ankieta ogólna  typ studiów: licencjackie  id: 2  11304577320893268228391420576688236555476517901921754212130727677604240925772204231973812110326287676033501333114085724038333343931171186288596112485688378  31734325192917143944466127908890793821179582586626629958226855693777598793367785088947241788110381050955523196190991176574965873455664272162371790386537647647432744486649188767324069823118147246454621182364395747288277369384288450930143315750566738592059298898717724782661738514467974355581398302460061546390  ----------------------------------  [ankieta 3 ogólna]Ankieta ogólna  typ studiów: licencjackie  id: 3  11304577320893268228391420576688236555476517901921754212130727677604240925772204231973812110326287676033501333114085724038333343931171186288596112485688378  5890310371368579728529936494695697291916594418618939506527005778579354982808769191690974801164596847812594441334437394335547633610902070335427969354244661483665096783538404837117253153860295262624245892602695924134581879503641368697574244133876685188873811936223451168314508375535406976656929700659589812819  ---------------------------------- " |
    
    Scenario Outline: Failure - none of the tickets are properly signed
        When I follow "Oceń zajęcia"
        And I fill in "Podaj wygenerowane bilety:" with <bad_ticket>
        And I press "Wyślij"
        Then I should see "Nie udało się zweryfikować podpisu pod biletem."  

        Examples:
            | bad_ticket                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
            | "[Ankieta 2]Ankieta ogólna  typ studiów: licencjackie  id: 2  11304577320893268228391420576688236555476517901921754212130727677604240925772204231973812110326287676033501333114085724038333343931171186288596112485688378  31734325192917143944466127908890793821179582586626629958226855693777598793367785088947241788110381050955523196190991176574965873455664272162371790386537647647432744486649188767324069823118147246454621182364395747288277369384288450930143315750565738592059298898717724782661738514467974355581398302460061546390  ----------------------------------  [ankieta 3 ogólna]Ankieta ogólna  typ studiów: licencjackie  id: 3  11304577320893268228391420576688236555476517901921754212130727677604240925772204231973812110326287676033501333114085724038333343931171186288596112485688378  58903103713685797285299364946956972919165944186189395065270057785793549828087691916909748011645968478125944413344373943355476336109020703354279693542446614836650967835384048371172531538602952626242458926026959241345818795036413686975742441338766851888738119362234511683145083755354069766569297006592189812815  ---------------------------------- " |
      
