# encoding: utf-8
require 'uri'
require 'cgi'

Given /^I enroll in "([^"]*)" in group with id "([^"]*)"$/ do |coursename, id|
   Given %{I am on courses page}
     And %{I click on "#{coursename}"}
     And %{I sleep for 10 seconds} 
     And %{I press "zapisz" next to "group-id" with value "#{id}"}
end

When /^I pin the group "([^"]*)" near "([^"]*)"$/ do |text1, text2|
  place = page.find(:xpath, "//*[text()=\"#{text2}\"]/following-sibling::*[text()=\"#{text1}\"]")
  #place.native.hover()
  place.find(:xpath, "following-sibling::div/span[@title=\"przypnij do planu\"]" ).click
end

When /^I enroll in a pinned group "([^"]*)"$/ do |gid|
   page.find(:xpath, "//div[@id=\"schedule-term-#{gid}-#{gid}\"]/div/div/div/div[@title=\"Zapisz\"]").click
end
