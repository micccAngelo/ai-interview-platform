# frozen_string_literal: true

class FitGapGeneratorWorker
  include Sidekiq::Worker

  sidekiq_options queue: :default, retry: 2

  def perform(portfolio_id, vacancy_id)
    portfolio = Portfolio.find(portfolio_id)
    vacancy   = Vacancy.unscoped.find(vacancy_id)

    FitGap::Engine.new(portfolio: portfolio, vacancy: vacancy).call
  rescue ActiveRecord::RecordNotFound => e
    Rails.logger.warn('[N13] Record not found or tenant mismatch')
  rescue StandardError => e
    Rails.logger.error("[N13] fitgap_failed portfolio_id=#{portfolio_id} vacancy_id=#{vacancy_id} error_class=#{e.class.name}")
    raise
  end
end
