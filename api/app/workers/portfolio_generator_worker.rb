# frozen_string_literal: true

class PortfolioGeneratorWorker
  include Sidekiq::Worker

  sidekiq_options queue: :portfolio, retry: 3

  sidekiq_retries_exhausted do |msg, _ex|
    session_id = msg['args'].first
    session = Session.unscoped.find_by(id: session_id)
    session&.with_lock do
      portfolio = session.reload.portfolio
      unless portfolio.nil? || portfolio.complete?
        portfolio.update!(generation_status: 'failed',
          generation_error: 'Generation could not be completed after retries. Please retry or contact an assessor.')
        Rails.logger.error("[N10] Portfolio generation permanently failed for session #{session_id}")
      end
    end
  end

  def perform(session_id)
    session = Session.unscoped.find(session_id)
    Current.using(tenant_id: session.tenant_id) do
      Portfolios::Generator.new(session: session).call
    end
  rescue ActiveRecord::RecordNotFound
    Rails.logger.warn("[N10] Session #{session_id} not found — skipping")
  end
end
