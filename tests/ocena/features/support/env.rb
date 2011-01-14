require 'rubygems'
require 'cucumber/formatter/unicode'
require 'selenium-webdriver'
require 'capybara/cucumber'

Capybara.default_driver = :selenium
#Capybara.app_host = "http://nowe-zapisy.ii.uni.wroc.pl"
Capybara.app_host = "http://localhost:8000"
 
#~ Before do
  #~ Fixtures.reset_cache
  #~ Fixtures.create_fixtures("fixtures", "users")
  #~ Fixtures.create_fixtures("fixtures", "subjects")
#~ end
