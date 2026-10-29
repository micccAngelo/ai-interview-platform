require 'rails_helper'
RSpec.describe 'Evidence review endpoints', type: :request do
  before { domain; generate }
  it 'returns real integer and null levels with assessment status' do
    get "/api/v1/sessions/#{@session.id}/portfolio", headers: auth_headers
    expect(response).to have_http_status(:ok)
    rows = JSON.parse(response.body).fetch('portfolio').fetch('skills')
    expect(rows.find { |row| row['skill_id'] == 'react' }).to include('ai_level' => 3, 'assessment_status' => 'assessed')
    expect(rows.find { |row| row['skill_id'] == 'sql' }).to include('ai_level' => nil, 'assessment_status' => 'not_assessed')
  end
  it 'does not expose historical raw provider errors' do
    @portfolio.update!(generation_status: 'failed', generation_error: 'private historical provider response')
    get "/api/v1/sessions/#{@session.id}/portfolio", headers: auth_headers
    expect(response).to have_http_status(:ok)
    expect(response.body).not_to include('private historical')
  end
  it 'blocks foreign portfolio, export, fitgap and override IDs' do
    foreign = Organization.create!(name: 'Other synthetic tenant', scheme: 'other-synthetic', identifier: 'other-synthetic', host: 'other.example.test')
    headers = auth_headers(foreign)
    skill = @portfolio.portfolio_skills.first
    get "/api/v1/portfolios/#{@portfolio.id}/export", headers: headers
    expect(response).to have_http_status(:not_found)
    get "/api/v1/portfolios/#{@portfolio.id}/fitgap/#{@vacancy.id}", headers: headers
    expect(response).to have_http_status(:not_found)
    post "/api/v1/portfolio_skills/#{skill.id}/override", params: { override: { override_level: 4, assessor_notes: 'Cannot cross tenant.' } }, headers: headers
    expect(response).to have_http_status(:not_found)
    expect(skill.reload.assessor_override).to be_nil
  end
  it 'rejects candidate roles from assessor evidence' do
    get "/api/v1/sessions/#{@session.id}/portfolio", headers: auth_headers(role: 'student')
    expect(response).to have_http_status(:forbidden)
  end
  it 'does not let a tenant header repair a token without an organization claim' do
    token = JsonWebToken.encode(user_id: 9001, role: 'admin')
    get "/api/v1/sessions/#{@session.id}/portfolio", headers: { 'Authorization' => "Bearer #{token}", 'X-Tenant-Scheme' => @organization.scheme }
    expect(response).to have_http_status(:forbidden)
  end
  it 'exports the same unassessed semantics in a real PDF' do
    get "/api/v1/portfolios/#{@portfolio.id}/export", params: { format: 'pdf', vacancy_id: @vacancy.id }, headers: auth_headers
    expect(response).to have_http_status(:ok)
    expect(response.media_type).to eq('application/pdf')
    expect(response.body).to start_with('%PDF')
  end
  it 'requires a rationale and refuses to guess an unassessed level' do
    skill = @portfolio.portfolio_skills.find_by!(skill_id: 'react')
    post "/api/v1/portfolio_skills/#{skill.id}/override", params: { override: { override_level: 4, assessor_notes: '' } }, headers: auth_headers
    expect(response).to have_http_status(:unprocessable_entity)
    skill = @portfolio.portfolio_skills.find_by!(skill_id: 'sql')
    post "/api/v1/portfolio_skills/#{skill.id}/override", params: { override: { override_level: 4, assessor_notes: 'A guess is not evidence.' } }, headers: auth_headers
    expect(response).to have_http_status(:unprocessable_entity)
  end
  it 'saves an override and recomputes comparison without a model call' do
    skill = @portfolio.portfolio_skills.find_by!(skill_id: 'react')
    get "/api/v1/portfolios/#{@portfolio.id}/fitgap/#{@vacancy.id}", headers: auth_headers
    post "/api/v1/portfolio_skills/#{skill.id}/override", params: { override: { override_level: 4, assessor_notes: 'Reviewed supporting evidence.' } }, headers: auth_headers
    expect(response).to have_http_status(:ok)
    get "/api/v1/portfolios/#{@portfolio.id}/fitgap/#{@vacancy.id}", headers: auth_headers
    expect(JSON.parse(response.body)['report']['skill_comparisons'].first).to include('candidate_level' => 4, 'expected_level' => 3)
  end
  it 'keeps failed status retryable when queueing fails' do
    @portfolio.update!(generation_status: 'failed')
    allow(PortfolioGeneratorWorker).to receive(:perform_async).and_raise(StandardError, 'private provider detail')
    post "/api/v1/sessions/#{@session.id}/portfolio/regenerate", headers: auth_headers
    expect(response).to have_http_status(:service_unavailable)
    expect(@portfolio.reload.generation_status).to eq('failed')
    expect(response.body).not_to include('private provider detail')
  end
  it 'disables the standalone tenant-selecting login by default' do
    post '/api/v1/auth/login', params: { email: 'synthetic@example.test', password: 'not-a-real-password' }, headers: { 'X-Tenant-Scheme' => 'other' }
    expect(response).to have_http_status(:forbidden)
  end
end
