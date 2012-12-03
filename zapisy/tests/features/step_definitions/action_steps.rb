# encoding: utf-8
require 'uri'
require 'cgi'

module WithinHelpers
	def with_scope(locator)
		locator ? within(locator) { yield } : yield
	end
end
World(WithinHelpers)

Given /^(?:|I )am on (.+)$/ do |page|
	visit path_to(page)
end

When /^(?:|I )go to (.+)$/ do |url|
	visit url
end

When /^(?:|I )press "([^"]*)"$/ do |button|
	click_button(button)
end

When /^(?:|I )press visible "([^"]*)"$/ do |button|
    page.find(:xpath, "//*[input[(@value='#{button}')]]", :visible => true ).click_button(button)
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

When /^I click "([^"]*)"$/ do |value|
    selector = "//*[contains(text(),'#{value}') or @alt='#{value}']"
    page.find(:xpath, selector).click
end

When /^I click on link which points to "([^"]*)"$/ do |path|
  page.find(:xpath, "//a[@href=\"#{path}\"]").click
end

When /^(?:|I )fill in "([^"]*)" with "([^"]*)"$/ do |field, value|
	value.gsub!(/\n/, '<br/>')
	fill_in(field, :with => value)
end

When /^(?:|I )fill in "([^"]*)" with value "([^"]*)" with "([^"]*)"$/ do |field, value_no, value|
    value.gsub!(/\n/, '<br/>')
    page.find( :xpath, "//*[input[(@name='#{field}') and (@id='#{value_no}')]]" ).fill_in(field, :with => value)
end

When /^(?:|I )select "([^"]*)" as "([^"]*)"$/ do |field, value|
  select(value, :from => field )
end

When /^(?:|I )choose "([^"]*)" as "([^"]*)"$/ do |field, value|
    choose(value)
end

When /^(?:|I )check "([^"]*)"$/ do |field|
    check(field)
end

When /^(?:|I )uncheck "([^"]*)"$/ do |field|
    uncheck(field)
end

When /^(?:|I )check "([^"]*)" with value "([^"]*)"$/ do |field, value|
    page.find(:xpath, "//*[input[(@name='#{field}') and (@value='#{value}')]]" ).check(field)
end

Then /^show me the page$/ do
    save_and_open_page
end

When /^I press "([^"]*)" in warning window$/ do |arg1|
  page.click_link_or_button(arg1)
end


