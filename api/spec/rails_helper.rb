ENV['RAILS_ENV'] ||= 'test'
ENV['SECRET_KEY_BASE'] ||= 'test-only-signing-value-do-not-deploy'
ENV['ALLOWED_ORIGINS'] ||= 'http://localhost:5173'
require File.expand_path('../config/environment', __dir__)
require 'rspec/rails'
Rack::Attack.cache.store = ActiveSupport::Cache::MemoryStore.new
ActiveRecord::Migration.maintain_test_schema!
Dir[Rails.root.join('spec/support/**/*.rb')].sort.each { |file| require file }
RSpec.configure do |config|
  config.use_transactional_fixtures = true
  config.include AssessmentFixtures
  config.before { Current.clear }
  config.after { Current.clear }
  config.order = :random
end
