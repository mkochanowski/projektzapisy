# encoding: utf-8
require 'uri'
require 'cgi'

def load_fixture(fixture)
    path = "../"
    system "#{path}manage.py loaddata #{path}tests/fixtures/#{fixture}.json -v 0"
end

Given /I start new scenario for "([^"]*)"/ do |fereol_part|
    path = "../"
    system "#{path}manage.py flush --noinput -v 0"
    system "#{path}manage.py migrate --fake -v 0"
    case fereol_part
        when 'enrollment' 
            load_fixture("core_dump_enrollment")
        when 'grade' 
            load_fixture("core_dump_grade")
        when 'offer' 
            load_fixture("core_dump_offer")
    end
end

### GRADE FIXTURES ###

Given /^the grading protocol is "([^"]*)"$/ do |state|
	if state == "on"
		load_fixture("grade/grade_active")
	elsif state == "off"
		load_fixture("grade/grade_not_active")
	end
end

Given /^there are polls generated$/ do
	load_fixture "grade/groups"
	load_fixture "grade/polls"
end

Given /^there are templates generated$/ do
	load_fixture "grade/groups"
	load_fixture "grade/polls"
	load_fixture "grade/templates"
end

Given /^there are keys generated for polls$/ do
	load_fixture "grade/keys_for_polls"
end

When /^I add new poll$/ do
	load_fixture "grade/new_poll"
end

Given /^I am signed for groups with polls$/ do
	load_fixture "grade/groups"
	load_fixture "grade/polls"
	load_fixture "grade/records"
    load_fixture "grade/keys_for_polls"
end

Given /^there are some courses with groups for current semester$/ do
	load_fixture "grade/groups"
	load_fixture "grade/records"
end

Given /^there are some sections created already$/ do
	load_fixture "grade/groups"
	load_fixture "grade/sections"
end

Given /^there is a poll for some exercises$/ do
    load_fixture "grade/exercises_przedmiot_4"
end

Given /^there are courses without a poll$/ do
  load_fixture "grade/new_course"
end

