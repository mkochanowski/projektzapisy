module NavigationHelpers
  # Maps a name to a path. Used by the
  #
  #   When /^I go to (.+)$/ do |page_name|
  #
  # step definition in web_steps.rb
  #
  def path_to(page_name)
    case page_name

    when /the home\s?page/
      '/'
      
    when /my profile page/
      '/users/'

    when /the mobile home page/
      'http://m.localhost.localhost:8000/'
      
    when /subjects page/
      '/subjects/'
      
    when /schedule page/
      '/records/schedule/'
    
    when /schedule prototype page/
       '/records/schedule/prototype/'
    
    else
          begin
            page_name =~ /the (.*) page/
            path_components = $1.split(/\s+/)
            self.send(path_components.push('path').join('_').to_sym)
          rescue Object => e
            raise "Can't find mapping from \"#{page_name}\" to a path.\n" +
              "Now, go and add a mapping in #{__FILE__}"
          end
        end
      end
    end

    World(NavigationHelpers)
