# encoding: utf-8
require 'uri'
require 'cgi'

Then /^I enroll to group with id "([^"]*)" on mobile$/ do |gid|
  page.find(:xpath, "//form[@action=\"\/group\/#{gid}\/assign\/\"]/input").click
end

Then /^I unenroll to group with id "([^"]*)" on mobile$/ do |gid|
  page.find(:xpath, "//form[@action=\"\/group\/#{gid}\/resign\/\"]/input").click
end
