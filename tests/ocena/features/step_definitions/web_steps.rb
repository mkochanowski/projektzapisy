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
    system "#{path}manage.py loaddata #{path}tests/ocena/fixtures/#{fixture}.json -v 0"
end

def run_client(input_file)
    path = "../../site_media/Downloads/"
    system "rm -rf tickets.txt"
    system "python #{path}client.py < client_input/#{input_file} > out"
    system "rm -rf out"
end

Given /I start new scenario/ do
    path = "../../"
    system "#{path}manage.py flush --noinput -v 0"
    system "#{path}manage.py migrate --fake -v 0"
    system "#{path}manage.py loaddata #{path}tests/ocena/fixtures/core_dump.json -v 0"
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

Then /^"([^\"]+)" should be invisible$/ do |text|
  paths = [
    "//*[@class='hidden']/*[contains(.,'#{text}')]",
    "//*[@class='invisible']/*[contains(.,'#{text}')]",
    "//*[@style='display: none;']/*[contains(.,'#{text}')]"
  ]
  xpath = paths.join '|'
  page.should have_xpath(xpath)
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

When /^(?:|I )press visible "([^"]*)"$/ do |button|
    page.find(:xpath, "//*[input[(@value='#{button}')]]", :visible => true ).click_button(button)
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

Then /^I cannot check "([^"]*)"$/ do |field|
    page.find(:xpath, "//*[input[(@id='#{field}' or @name='#{field}') and @disabled]]")
end

Then /^"([^"]*)" should be disabled$/ do |field|
    page.find(:xpath, "//*[input[(@id='#{field}' or @name='#{field}' or @value='#{field}') and @disabled]]")
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

Given /^there are some subjects with groups for current semester$/ do
	load_fixture "groups"
	load_fixture "records"
end

Given /^there are some sections created already$/ do
	load_fixture "groups"
	load_fixture "sections"
end

Given /^there is a poll for some exercises$/ do
    load_fixture "exercises_przedmiot_4"
end

When /^I uncheck "([^"]*)" checkboxes in tickets grouping options$/ do |arg|
	if arg == "all" then
		# odznaczenie obu checkboxów
		uncheck("join_1")
		uncheck("join_2")		
	elsif arg == "some" then
		# odznaczenie pierwszego checkboxa (w teście są dwa)	
		uncheck("join_1")
	elsif arg == "no" then
		# we do not touch anything then
	end
end

Then /^I wait for a while to see "([^"]*)"$/ do |text|  
    sleep 10
    wait_until(5) { page.should have_content(text) }
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

When /^I click "([^"]*)"$/ do |value|
    selector = "//*[contains(text(),'#{value}') or @alt='#{value}']"
    page.find(:xpath, selector).click
end

When /^I run client with "([^"]*)"$/ do |file|
    run_client( file )
end
