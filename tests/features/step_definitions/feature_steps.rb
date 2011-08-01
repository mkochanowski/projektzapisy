# encoding: utf-8
require 'uri'
require 'cgi'

Given /I am logged in with "([^"]*)" privileges$/ do |privileges|
  Given %{I am on the home page}
    And %{I follow "Ocena zajęć"}
    And %{I follow "Zaloguj"}
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

Given /I am logged in$/ do
  Given %{I am on the home page} 
    And %{I follow "Zaloguj"}
    And %{I fill in "Nazwa użytkownika" with "student-test"}
    And %{I fill in "Hasło" with "aaa"}
    And %{I press "Zaloguj"}
end
