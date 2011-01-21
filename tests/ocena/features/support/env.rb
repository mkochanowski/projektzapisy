require 'rubygems'
require 'cucumber/formatter/unicode'
require 'selenium-webdriver'
require 'capybara/cucumber'

Capybara.default_driver = :selenium
#Capybara.app_host = "http://nowe-zapisy.ii.uni.wroc.pl"
Capybara.app_host = "http://localhost:8000"

def load_fixture(fixture)
    path = "../../"
    system "#{path}manage.py loaddata #{path}tests/ocena/fixtures/#{fixture}.json"
end
