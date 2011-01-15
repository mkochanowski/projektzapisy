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
		
	elsif state == "off"
		
	end
end

Then /^(?:|I )should see link "([^"]*)"$/ do |link|  
	page.should have_content(link)
	#powinno być też sprawdzanie, czy to jest link..
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
