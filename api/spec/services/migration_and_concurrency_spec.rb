require 'rails_helper'
require Rails.root.join('db/migrate/20261029000001_preserve_unassessed_portfolio_skills')
RSpec.describe PreserveUnassessedPortfolioSkills, type: :model do
  before { domain }
  after { PortfolioSkill.reset_column_information }
  it 'round-trips legacy data without changing its original score' do
    original = @portfolio.portfolio_skills.create!(skill_label: 'Legacy score', ai_level: 2, ai_confidence: 'low', competency_summary: 'Historical model output.')
    described_class.new.down
    described_class.new.up
    PortfolioSkill.reset_column_information
    expect(original.reload.ai_level).to eq(2)
    expect(original.assessment_status).to eq('legacy')
  end
  it 'refuses a destructive rollback while unassessed rows exist' do
    generate
    expect { described_class.new.down }.to raise_error(ActiveRecord::IrreversibleMigration, /never invent ratings/)
    expect(@portfolio.portfolio_skills.find_by!(skill_id: 'sql').ai_level).to be_nil
  end
  it 'enforces rating and status consistency at the database boundary' do
    generate
    skill = @portfolio.portfolio_skills.find_by!(skill_id: 'react')
    expect do
      PortfolioSkill.transaction(requires_new: true) { skill.update_columns(ai_level: nil, assessment_status: 'assessed') }
    end.to raise_error(ActiveRecord::StatementInvalid)
    expect(skill.reload.ai_level).to eq(3)
  end
end

RSpec.describe 'Concurrent duplicate portfolio jobs', type: :model do
  self.use_transactional_tests = false
  before { domain }
  after do
    @session&.destroy!
    @assessment&.destroy!
    @vacancy&.destroy!
    @organization&.destroy!
  end
  it 'calls the model once and publishes one complete result under two workers' do
    response = payload
    mutex = Mutex.new
    calls = 0
    client = Object.new
    client.define_singleton_method(:generate_content) do |*_args, **_options|
      mutex.synchronize { calls += 1 }
      sleep 0.2
      response
    end
    session_id = @session.id
    gate = Queue.new
    threads = 2.times.map do
      Thread.new do
        gate.pop
        ActiveRecord::Base.connection_pool.with_connection do
          Portfolios::Generator.new(session: Session.unscoped.find(session_id), gemini_client: client).call.id
        end
      end
    end
    2.times { gate << true }
    expect(threads.map(&:value).uniq).to eq([@portfolio.id])
    expect(calls).to eq(1)
    expect(@portfolio.reload.generation_status).to eq('complete')
    expect(@portfolio.portfolio_skills.count).to eq(2)
  end
end
