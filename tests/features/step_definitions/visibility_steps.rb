# encoding: utf-8
require 'uri'
require 'cgi'

Then /^(?:|I )should see link "([^"]*)"$/ do |link|  
	page.should have_link(link)
end

Then /^(?:|I )should see link "([^"]*)"$/ do |text|
  find_link(text).visible?
end

Then /^(?:|I )should see "([^"]*)"$/ do |text|  
	page.should have_content(text)
end

Then /^(?:|I )should see "([^"]*)"(?: within "([^"]*)")$/ do |text, selector|
  with_scope(selector) do
    page.should have_content(text)    
  end
end

Then /^(?:|I )should not see link "([^"]*)"$/ do |link|  
  page.should have_no_link(link)
end

Then /^(?:|I )should not see "([^"]*)"$/ do |text|  
    sleep 5
    page.should have_no_content(text)
end

Then /^"([^\"]+)" should be invisible$/ do |text|
  paths = [
    "//*[@class='hidden']/*[contains(.,'#{text}')]",
    "//*[@class='invisible']/*[contains(.,'#{text}')]",
    "//*[@style='display: none;']/*[contains(.,'#{text}')]"
  ]
  xpath = paths.join '|'
  page.should have_xpath(xpath)
end

Then /^(?:|I )should see button "([^"]*)" next to "([^"]*)" with value "([^"]*)"$/ do |button, name, value|
    page.should have_xpath("//*[@name=\"#{name}\" and @value=\"#{value}\"]/following-sibling::input[@type=\"button\" and @value=\"#{button}\"]")
end


#[TODO: czemu find a nie should have_xpath?]
Then /^I cannot check "([^"]*)"$/ do |field|
    page.find(:xpath, "//*[input[(@id='#{field}' or @name='#{field}') and @disabled]]")
end

#[TODO: czemu find a nie should have_xpath?]
Then /^"([^"]*)" should be disabled$/ do |field|
    page.find(:xpath, "//*[input[(@id='#{field}' or @name='#{field}' or @value='#{field}') and @disabled]]")
end

Then /^I should be on (.+)$/ do |page_name|  
	current_path = URI.parse(current_url).path
	current_path.should == path_to(page_name)
end

Then /^I should see a warning "([^"]*)"$/ do |arg1|
  page.should have_content(arg1)
end

Then /^I wait for a while to see "([^"]*)"$/ do |text|  
    sleep 5
    wait_until(10) { page.should have_content(text) }
end

Then /^"([^"]*)" should be filled with "([^"]*)"$/ do |field, value|
    find_field(field).value.should == value
end

Then /^"([^"]*)" should be hidden$/ do |field|
    page.should have_xpath("//*[input[(@name='#{field}') and (@style='display: none;')]]")
end

Then /^"([^"]*)" should be checked$/ do |field|
    page.should have_checked_field( field )
end

Then /^"([^"]*)" should be unchecked$/ do |field|
     page.should have_unchecked_field( field )
end

Then /^I can select from "([^"]*)" options in "([^"]*)"$/ do |number, field|
	page.has_select? field, :count=>number
end

Then /^I can select "([^"]*)" as "([^"]*)"$/ do |value, field|
	page.has_select? field, :options =>[value]
end

Then /^I can not select "([^"]*)" from "([^"]*)"$/ do |value, field|
	page.has_no_select? field, :options =>[value]
end

Then /^I should see "([^"]*)" near "([^"]*)"$/ do |text1, text2|
    page.should have_xpath("//*[text()=\"#{text2}\"]/following-sibling::*[text()=\"#{text1}\"]")
end

Then /^I should see link which points to "([^"]*)"$/ do |path|
   page.should have_xpath("//a[@link=\"#{path}\"]")
end
