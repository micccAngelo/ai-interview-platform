# frozen_string_literal: true

class PortfolioSkill < ApplicationRecord
  CONFIDENCE_LEVELS = %w[high medium low].freeze

  belongs_to :portfolio
  has_one :assessor_override, dependent: :destroy

  validates :skill_label, presence: true
  validates :ai_level, numericality: { only_integer: true, in: 1..5 }, allow_nil: true
  validates :assessment_status, inclusion: { in: %w[assessed not_assessed legacy] }
  validate :rating_matches_status
  validates :ai_confidence, inclusion: { in: CONFIDENCE_LEVELS }
  validates :competency_summary, presence: true

  # evidence is stored as JSONB array of quote strings
  def evidence_quotes
    Array(evidence)
  end

  def assessed?
    assessment_status == 'assessed' && ai_level.is_a?(Integer) && (1..5).cover?(ai_level)
  end

  private

  def rating_matches_status
    if assessment_status == 'not_assessed' ? ai_level.present? : ai_level.nil?
      errors.add(:ai_level, 'must agree with assessment status')
    end
  end
end
