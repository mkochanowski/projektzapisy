# encoding: utf-8
require 'uri'
require 'cgi'

module WithinHelpers
  def with_scope(locator)
    locator ? within(locator) { yield } : yield
  end
end
World(WithinHelpers)


Given /I am logged in/ do
  Given %{I am on the home page}
    And %{I follow "System zapisów"}
    And %{I follow "Zaloguj"}
    And %{I fill in "Nazwa użytkownika" with "student-test"}
    And %{I fill in "Hasło" with "aaa"}
    And %{I press "Zaloguj"}
end

Given /^I enroll in "([^"]*)" in group with id "([^"]*)"$/ do |coursename, id|
   Given %{I am on subjects page}
     And %{I click on "#{coursename}"}
     And %{I click on link which points to "/records/#{id}/assign"}
end

Given /^(?:|I )am on (.+)$/ do |page|
  visit path_to(page)
#  sleep 10
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

Then /^(?:|I )should see "([^"]*)"(?: within "([^"]*)")$/ do |text, selector|
  with_scope(selector) do
    page.should have_content(text)    
  end
end

Then /^(?:|I )should see "([^"]*)"$/ do |text|  
  page.should have_content(text)
end

Then /^(?:|I )should not see "([^"]*)"$/ do |text|  
  sleep 10
  page.should have_no_content(text)
end

Then /^I should be on (.+)$/ do |page_name|  
  current_path = URI.parse(current_url).path
  current_path.should == path_to(page_name)
end

When /^I sleep for ([0-9]+) seconds$/ do |secs|
   sleep secs.to_i
end

When /^I click on link which points to "([^"]*)"$/ do |path|
  page.find(:xpath, "//a[@link=\"#{path}\"]").click
end

Then /^I should see link which points to "([^"]*)"$/ do |path|
   page.should have_xpath("//a[@link=\"#{path}\"]")
end

Then /^show me the page$/ do
  save_and_open_page
end
