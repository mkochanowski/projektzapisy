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
    system "#{path}manage.py loaddata #{path}tests/end2end/fixtures/#{fixture}.json -v 0"
end

Given /I start new scenario/ do
    path = "../../"
    system "#{path}manage.py flush --noinput -v 0"
    system "#{path}manage.py migrate --fake -v 0"
    system "#{path}manage.py loaddata #{path}tests/end2end/fixtures/core_dump.json -v 0"
end

Given /I am logged in/ do
  Given %{I am on the home page} 
    And %{I follow "Zaloguj"}
    And %{I fill in "Nazwa użytkownika" with "student-test"}
    And %{I fill in "Hasło" with "aaa"}
    And %{I press "Zaloguj"}
end

Given /^I enroll in "([^"]*)" in group with id "([^"]*)"$/ do |coursename, id|
   Given %{I am on courses page}
     And %{I click on "#{coursename}"}
     And %{I sleep for 10 seconds} 
     And %{I press "zapisz" next to "group-id" with value "#{id}"}
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

When /^(?:|I )press "([^"]*)" next to "([^"]*)" with value "([^"]*)"$/ do |button, name, value|
    page.find(:xpath, "//input[@name=\"#{name}\" and @value=\"#{value}\"]/following-sibling::input[@type=\"button\" and @value=\"#{button}\"]").click
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

Then /^(?:|I )should see button "([^"]*)" next to "([^"]*)" with value "([^"]*)"$/ do |button, name, value|
    page.should have_xpath("//*[@name=\"#{name}\" and @value=\"#{value}\"]/following-sibling::input[@type=\"button\" and @value=\"#{button}\"]")
end

Then /^(?:|I )should see "([^"]*)"$/ do |text|  
  page.should have_content(text)
end

Then /^(?:|I )should see link "([^"]*)"$/ do |text|
  find_link(text).visible?
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
  page.find(:xpath, "//a[@href=\"#{path}\"]").click
end

Then /^I should see link which points to "([^"]*)"$/ do |path|
   page.should have_xpath("//a[@link=\"#{path}\"]")
end

Then /^show me the page$/ do
  save_and_open_page
end

Then /^I enroll to group with id "([^"]*)" on mobile$/ do |gid|
  page.find(:xpath, "//form[@action=\"\/group\/#{gid}\/assign\/\"]/input").click
end

Then /^I unenroll to group with id "([^"]*)" on mobile$/ do |gid|
  page.find(:xpath, "//form[@action=\"\/group\/#{gid}\/resign\/\"]/input").click
end

When /^I pin the group "([^"]*)" near "([^"]*)"$/ do |text1, text2|
  place = page.find(:xpath, "//*[text()=\"#{text2}\"]/following-sibling::*[text()=\"#{text1}\"]")
  #place.native.hover()
  place.find(:xpath, "following-sibling::div/span[@title=\"przypnij do planu\"]" ).click
end

When /^I enroll in a pinned group "([^"]*)"$/ do |gid|
   page.find(:xpath, "//div[@id=\"schedule-term-#{gid}-#{gid}\"]/div/div/div/div[@title=\"Zapisz\"]").click
end

Then /^I should see "([^"]*)" near "([^"]*)"$/ do |text1, text2|
 page.should have_xpath("//*[text()=\"#{text2}\"]/following-sibling::*[text()=\"#{text1}\"]")
end
