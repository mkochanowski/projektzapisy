require 'rubygems'
require 'cucumber/formatter/unicode'
require 'selenium-webdriver'
require 'capybara/cucumber'

Capybara.default_driver = :selenium

Capybara.app_host = "http://localhost.localhost:8000"
Capybara.default_wait_time = 5 # we wait for 5 seconds until failing a test

Capybara.register_driver :selenium_remote_ie do |app|
   Capybara::Driver::Selenium.new(app, :browser => :remote, :desired_capabilities => :internet_explorer,
                                       :url => "http://10.0.2.2:4044/wd/hub") # 10.0.2.2 to jest host fereol-ci, z punktu widzenia Virtual-Ubuntu
end

Capybara.register_driver :selenium_local_chrome do |app|
   Capybara::Driver::Selenium.new(app, :browser => :chrome)
end

if ENV['BROWSER'] == "ie"
   Capybara.default_driver = :selenium_remote_ie
   Capybara.app_host = "http://10.0.2.2:4026" # 10.0.2.2 to jest host fereol-ci, z punktu widzenia maszyny Virtual-XP
   # w tym przypadku trzeba odpalać gunicorn_django z parametrem -b 0.0.0.0:8000, aby aplikacja przyjmowała żądania spoza localhosta
elsif ENV['BROWSER'] == "chrome"
   Capybara.default_driver = :selenium_local_chrome
else
   Capybara.default_driver = :selenium
end
