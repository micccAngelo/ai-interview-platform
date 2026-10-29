require 'rails_helper'
require 'faraday/adapter/test'
RSpec.describe Gemini::HttpClient, type: :model do
  it 'never logs a raw provider response body' do
    stubs = Faraday::Adapter::Test::Stubs.new do |stub|
      stub.post('/v1/models/test-model:generateContent') { [500, {}, 'private candidate transcript and provider detail'] }
    end
    connection = Faraday.new { |builder| builder.adapter :test, stubs }
    client = described_class.new(model: 'test-model', api_key: 'synthetic-test-only', retries: 0, connection: connection)
    messages = []
    allow(Rails.logger).to receive(:error) { |message| messages << message }
    expect { client.generate_content('synthetic input') }.to raise_error(described_class::ApiError)
    expect(messages.join).to include('status=500')
    expect(messages.join).not_to include('private candidate')
    stubs.verify_stubbed_calls
  end
  it 'recovers from a transient provider response with the real retry middleware' do
    stubs = Faraday::Adapter::Test::Stubs.new do |stub|
      stub.post('/v1/models/test-model:generateContent') { [503, { 'Retry-After' => '0' }, 'transient private response'] }
      stub.post('/v1/models/test-model:generateContent') { [200, {}, { candidates: [{ content: { parts: [{ text: '{"ok":true}' }] } }] }.to_json] }
    end
    client = described_class.new(model: 'test-model', api_key: 'synthetic-test-only', retries: 1)
    client.instance_variable_get(:@connection).adapter :test, stubs
    expect(client.generate_content('synthetic input')).to eq('ok' => true)
    stubs.verify_stubbed_calls
  end
end
