require 'rubygems'
require 'cucumber/formatter/unicode'
require 'selenium-webdriver'
require 'capybara/cucumber'

Capybara.default_driver = :selenium
Capybara.javascript_driver = :selenium
#Capybara.app_host = "http://nowe-zapisy.ii.uni.wroc.pl"
Capybara.app_host = "http://localhost.localhost:8000"
