# encoding: utf-8
require 'uri'
require 'cgi'

module WithinHelpers
	def with_scope(locator)
		locator ? within(locator) { yield } : yield
	end
end
World(WithinHelpers)

Given /I am logged in with "([^"]*)" privileges/ do |privileges|
  Given %{I am on the home page}
    And %{I follow "Ocena zajęć"}
    And %{I follow "zaloguj"}
    if privileges == "student" then
		And %{I fill in "Nazwa użytkownika" with "student-test"}
		And %{I fill in "Hasło" with "student-test"}
	elsif privileges == "employee" then 
			And %{I fill in "Nazwa użytkownika" with "employee-test"}
			And %{I fill in "Hasło" with "employee-test"}		
	elsif privileges == "administrator" then 
			And %{I fill in "Nazwa użytkownika" with "administrator-test"}
			And %{I fill in "Hasło" with "administrator-test"}		
	end    
    And %{I press "Zaloguj"}	
end

Given /^the grading protocol is "([^"]*)"$/ do |state|
	if state == "on"
		# fixtures: grade_active.json
	elsif state == "off"
		# fixtures: grade_not_active.json
	end
end

Then /^(?:|I )should see link "([^"]*)"$/ do |link|  
	page.should have_link(link)
end

Then /^(?:|I )should see "([^"]*)"$/ do |text|  
	page.should have_content(text)
end

Given /^(?:|I )am on (.+)$/ do |page|
	visit path_to(page)
end

When /^(?:|I )go to (.+)$/ do |url|
	visit url
end

When /^(?:|I )press "([^"]*)"$/ do |button|
	click_button(button)
end

When /^(?:|I )follow "([^"]*)"$/ do |link|
	click_link(link)
end

When /^(?:|I )click on "([^"]*)"$/ do |link|
	page.find(:xpath, "//*[text()=\"#{link}\"]").click
end

When /^(?:|I )fill in "([^"]*)" with "([^"]*)"$/ do |field, value|
	fill_in(field, :with => value)
end

Then /^I should be on (.+)$/ do |page_name|  
	current_path = URI.parse(current_url).path
	current_path.should == path_to(page_name)
end

When /^I sleep for ([0-9]+) seconds$/ do |secs|
    sleep secs.to_i
end

Then /^show me the page$/ do
    save_and_open_page
end

Given /^there are polls generated$/ do
	# fixtures: groups.json, polls.json
end

Given /^there are keys generated for polls$/ do
	# fixtures:  keys_for_polls.json
end

When /^I add new poll$/ do
	# stworzenie nowej ankiety w kodzie
end

Given /^I am signed for groups with polls$/ do
	# fixtures: groups.json, polls.json, records.json, keys_for_polls.json
end

When /^I uncheck "([^"]*)" checkboxes$/ do |arg|
	if arg == "all" then
		# odznaczenie obu checkboxów
		uncheck("join_common")
		uncheck("join_1")		
	elsif arg == "some" then
		# odznaczenie pierwszego checkboxa (w teście są dwa)	
		uncheck("join_common")
	elsif arg == "no" then
		# we do not touch anything then
	end
end

