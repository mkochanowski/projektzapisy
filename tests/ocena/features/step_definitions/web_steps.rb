# encoding: utf-8
require 'uri'
require 'cgi'

module WithinHelpers
	def with_scope(locator)
		locator ? within(locator) { yield } : yield
	end
end
World(WithinHelpers)

def load_fixture(fixture)
    path = "../../"
    system "#{path}manage.py loaddata #{path}tests/ocena/fixtures/#{fixture}.json"
end

Given /I start new scenario/ do
    path = "../../"
    system "#{path}manage.py flush --noinput"
    system "#{path}manage.py loaddata #{path}tests/ocena/fixtures/core_dump.json"
end

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
		load_fixture("grade_active")
	elsif state == "off"
		load_fixture("grade_not_active")
	end
end

Then /^(?:|I )should see link "([^"]*)"$/ do |link|  
	page.should have_link(link)
end

Then /^(?:|I )should see "([^"]*)"$/ do |text|  
	page.should have_content(text)
end

Then /^(?:|I )should not see link "([^"]*)"$/ do |link|  
  page.should have_no_link(link)
end

Then /^(?:|I )should not see "([^"]*)"$/ do |text|  
  page.should have_no_content(text)
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
	value.gsub!(/\n/, '<br/>')
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
	load_fixture "groups"
	load_fixture "polls"
end

Given /^there are keys generated for polls$/ do
	load_fixture "keys_for_polls"
end

When /^I add new poll$/ do
	load_fixture "new_poll"
end

Given /^I am signed for groups with polls$/ do
	load_fixture "groups"
	load_fixture "polls"
	load_fixture "records"
    load_fixture "keys_for_polls"
end

When /^I uncheck "([^"]*)" checkboxes in tickets grouping options$/ do |arg|
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

Given /^I have previously saved some data in polls using "([^"]*)"$/ do |ticket|
  #  provide fixture or use this ticket to fill a fake poll in polls filling test ;)
end

Then /^I wait for a while to see "([^"]*)"$/ do |text|  
    wait_until(15) { page.should have_content("text") }
end
