Feature: Behaviour of the system when someone tries to do something they do not have permission to do

	Background:
        Given I start new scenario      

    Scenario: Student wants to open grade
    Scenario: Student wants to close grade
    
    Scenario: Employee wants to open grade
    Scenario: Employee wants to close grade
    
    Scenario: Administrator wants to open grade when it is already opened
    Scenario: Administrator wants to close grade when it is already closed
    
    Scenario: Administrator wants to delete some polls when the grading protocol is on
    Scenario: Administrator wants to edit some polls when the grading protocol is on
    Scenario: Administrator wants to add some polls when the grading protocol is on

    Scenario: Student tries to add a poll
    Scenario: Student tries to delete a poll
    Scenario: Student tries to edit a poll    
    
    Scenario: Administrator wants to delete some sections when the grading protocol is on
    Scenario: Administrator wants to edit some sections when the grading protocol is on
    Scenario: Administrator wants to add some sections when the grading protocol is on

    Scenario: Student tries to add a section
    Scenario: Student tries to delete a section
    Scenario: Student tries to edit a section
    Scenario: Student tries to create tickets for polls when the protocol is off
