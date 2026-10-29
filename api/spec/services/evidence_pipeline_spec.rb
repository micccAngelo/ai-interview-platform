require 'rails_helper'
RSpec.describe Portfolios::ResponseValidator, type: :model do
  before { domain }
  def validate(data = payload)
    described_class.new(session: @session).call(data)
  end
  it 'includes omitted configured skills without inventing a rating' do
    rows = validate
    expect(rows.map { |row| row[:skill_label] }).to eq(%w[React SQL])
    expect(rows.last).to include(ai_level: nil, assessment_status: 'not_assessed', assessment_reason: 'omitted_by_model')
    expect(rows.first).to include(ai_level: 3, assessment_status: 'assessed')
  end
  [nil, '3', 3.5, true, false, 0, 6, {}, []].each do |invalid|
    it "does not coerce #{invalid.inspect} into a rating" do
      data = payload; data['configured_skills'][0]['level'] = invalid
      expect(validate(data).first).to include(ai_level: nil, assessment_reason: 'invalid_rating')
    end
  end
  it 'does not accept interviewer-only evidence' do
    data = payload; data['configured_skills'][0]['evidence'] = ['This sentence comes only from the interviewer and is not evidence.']
    expect(validate(data).first).to include(ai_level: nil, assessment_reason: 'unverified_evidence')
  end
  it 'does not accept invented quotes' do
    data = payload; data['configured_skills'][0]['evidence'] = ['I led a team of two hundred developers.']
    expect(validate(data).first[:ai_level]).to be_nil
  end
  it 'normalizes whitespace when checking candidate provenance' do
    data = payload; data['configured_skills'][0]['evidence'] = [AssessmentFixtures::QUOTE.gsub(' ', "\n")]
    expect(validate(data).first[:ai_level]).to eq(3)
  end
  it 'caps confidence using coverage rather than trusting the model' do
    @session.coverage_maps.find_by!(skill_id: 'react').update!(state: 'initiated', probe_count: 1)
    expect(validate.first[:ai_confidence]).to eq('low')
  end
  it 'never rates an untouched skill even when the model claims evidence' do
    @session.coverage_maps.find_by!(skill_id: 'react').update!(state: 'not_yet', probe_count: 0)
    expect(validate.first).to include(ai_level: nil, assessment_reason: 'not_explored')
  end
  it 'rejects duplicate identities, unknown skills and malformed payloads' do
    invalid = [nil, [], '{', { 'configured_skills' => {}, 'discovered_skills' => [] }]
    duplicate = payload; duplicate['configured_skills'] *= 2; invalid << duplicate
    unknown = payload; unknown['configured_skills'][0]['skill_id'] = 'unconfigured'; invalid << unknown
    invalid.each { |data| expect { validate(data) }.to raise_error(described_class::InvalidResponse) }
  end
  it 'does not expose an oversized or missing model summary' do
    data = payload; data['configured_skills'][0]['competency_summary'] = 'x' * 6001
    expect(validate(data).first[:assessment_reason]).to eq('invalid_summary')
  end
end

RSpec.describe Portfolios::Generator, type: :model do
  before { domain }
  it 'commits the complete validated portfolio and skips duplicate jobs' do
    client = double('model'); expect(client).to receive(:generate_content).once.and_return(payload)
    2.times { described_class.new(session: @session, gemini_client: client).call }
    expect(@portfolio.reload.generation_status).to eq('complete')
    expect(@portfolio.portfolio_skills.count).to eq(2)
    expect(@portfolio.portfolio_skills.find_by!(skill_id: 'sql').ai_level).to be_nil
  end
  it 'preserves existing results and stores a safe error on model failure' do
    original = @portfolio.portfolio_skills.create!(skill_id: 'old', skill_label: 'Original evidence', ai_level: 2, ai_confidence: 'low', competency_summary: 'Retain this record.')
    client = double('model'); allow(client).to receive(:generate_content).and_raise(Timeout::Error, 'private transcript or provider key')
    expect { described_class.new(session: @session, gemini_client: client).call }.to raise_error(Timeout::Error)
    expect(@portfolio.reload.generation_status).to eq('failed')
    expect(@portfolio.portfolio_skills.pluck(:id)).to eq([original.id])
    expect(@portfolio.generation_error).not_to include('private transcript')
  end
  it 'rolls back partial replacement writes if a later row fails' do
    original = @portfolio.portfolio_skills.create!(skill_label: 'Old record', ai_level: 2, ai_confidence: 'low', competency_summary: 'Preserve this record.')
    allow_any_instance_of(PortfolioSkill).to receive(:save!).and_wrap_original do |method, *args, **kwargs|
      raise ActiveRecord::RecordInvalid, method.receiver if method.receiver.skill_label == 'SQL'
      method.call(*args, **kwargs)
    end
    expect { generate }.to raise_error(ActiveRecord::RecordInvalid)
    expect(@portfolio.reload.generation_status).to eq('failed')
    expect(@portfolio.portfolio_skills.pluck(:id)).to eq([original.id])
  end
  it 'does not replace results when the model response shape is invalid' do
    expect { generate({}) }.to raise_error(Portfolios::ResponseValidator::InvalidResponse)
    expect(@portfolio.reload.generation_status).to eq('failed')
    expect(@portfolio.portfolio_skills).to be_empty
  end
end

RSpec.describe FitGap::Engine, type: :model do
  before { domain; generate }
  it 'preserves missing evidence as not_assessed and uses expected_level' do
    report = described_class.new(portfolio: @portfolio, vacancy: @vacancy).call
    expect(report.skill_comparisons.last).to include('expected_level' => 4, 'candidate_level' => nil, 'result' => 'not_assessed', 'delta' => nil)
    expect(report.culture_narrative).to be_nil
  end
  it 'does not match a different canonical identity by a shared label' do
    @vacancy.vacancy_skills.first.update!(skill_id: 'unrelated-id')
    report = described_class.new(portfolio: @portfolio, vacancy: @vacancy).call
    expect(report.skill_comparisons.first['result']).to eq('not_assessed')
  end
  it 'applies attributed overrides while retaining the original AI level' do
    skill = @portfolio.portfolio_skills.find_by!(skill_id: 'react')
    skill.create_assessor_override!(ai_level: 3, override_level: 4, assessor_notes: 'Verified the trade-off in context.', overridden_by: 9001)
    report = described_class.new(portfolio: @portfolio, vacancy: @vacancy).call
    expect(report.skill_comparisons.first).to include('candidate_level' => 4, 'result' => 'exceed', 'is_override' => true)
    expect(skill.reload.ai_level).to eq(3)
  end
  it 'rejects cross-tenant background work' do
    @vacancy.update!(tenant_id: @organization.id + 1)
    expect { described_class.new(portfolio: @portfolio, vacancy: @vacancy).call }.to raise_error(ActiveRecord::RecordNotFound)
  end
end

RSpec.describe PortfolioGeneratorWorker, type: :model do
  before { domain }
  it 'does not let an exhausted older job clobber a completed portfolio' do
    generate
    described_class.sidekiq_retries_exhausted_block.call({ 'args' => [@session.id], 'retry_count' => 3 }, nil)
    expect(@portfolio.reload.generation_status).to eq('complete')
  end
  it 'stores only a safe message when retries exhaust' do
    described_class.sidekiq_retries_exhausted_block.call({ 'args' => [@session.id], 'retry_count' => 3, 'error_message' => 'private provider response' }, nil)
    expect(@portfolio.reload.generation_status).to eq('failed')
    expect(@portfolio.generation_error).not_to include('private provider response')
  end
end

RSpec.describe 'Comparison edge cases', type: :model do
  before { domain; generate }
  it 'does not promote a legacy rating to assessed evidence' do
    @portfolio.portfolio_skills.find_by!(skill_id: 'react').update!(assessment_status: 'legacy')
    report = FitGap::Engine.new(portfolio: @portfolio, vacancy: @vacancy).call
    expect(report.skill_comparisons.first).to include('result' => 'not_assessed', 'candidate_level' => nil)
  end
  it 'matches canonical identifiers consistently across case differences' do
    @vacancy.vacancy_skills.first.update!(skill_id: 'REACT')
    report = FitGap::Engine.new(portfolio: @portfolio, vacancy: @vacancy).call
    expect(report.skill_comparisons.first['result']).to eq('match')
  end
  it 'does not choose arbitrarily between ambiguous custom labels' do
    ['Custom Craft', ' custom craft '].each do |label|
      @portfolio.portfolio_skills.create!(skill_label: label, ai_level: 3, ai_confidence: 'low', competency_summary: 'Synthetic custom evidence.', evidence: [AssessmentFixtures::QUOTE], assessment_status: 'assessed')
    end
    @vacancy.vacancy_skills.first.update!(skill_id: nil, skill_label: 'Custom Craft')
    report = FitGap::Engine.new(portfolio: @portfolio, vacancy: @vacancy).call
    expect(report.skill_comparisons.first).to include('result' => 'not_assessed', 'assessment_reason' => 'ambiguous_skill')
  end
  it 'rejects comparison without any vacancy requirements' do
    @vacancy.vacancy_skills.destroy_all
    expect { FitGap::Engine.new(portfolio: @portfolio, vacancy: @vacancy).call }.to raise_error(FitGap::Engine::NotReady)
  end
end
