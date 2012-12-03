# encoding: utf-8
require 'uri'
require 'cgi'

When /^I sleep for ([0-9]+) seconds$/ do |secs|
    sleep secs.to_i
end
