# frozen_string_literal: true

module FitGap
  class Engine
    class NotReady < StandardError; end
    def initialize(portfolio:, vacancy:)
      @portfolio = portfolio
      @vacancy = vacancy
    end

    def call
      session = Session.unscoped.find(@portfolio.session_id)
      raise ActiveRecord::RecordNotFound unless session.tenant_id == @vacancy.tenant_id

      @portfolio.with_lock do
        raise NotReady, 'Portfolio must be complete.' unless @portfolio.complete?
        raise NotReady, 'Add at least one vacancy skill requirement before comparing.' unless @vacancy.vacancy_skills.exists?

        comparisons = build_skill_comparisons
        report = FitGapReport.find_or_initialize_by(portfolio_id: @portfolio.id, vacancy_id: @vacancy.id)
        if report.new_record? || report.skill_comparisons != comparisons.as_json
          missing = comparisons.count { |row| row[:result] == 'not_assessed' }
          report.update!(skill_comparisons: comparisons, culture_narrative: nil,
            overall_narrative: "#{comparisons.size - missing} of #{comparisons.size} requirements have assessed evidence. #{missing} need follow-up. Skill comparisons support human review; they are not a hiring recommendation or a culture assessment.",
            generated_at: Time.current)
        end
        report
      end
    end

    private

    def build_skill_comparisons
      skills = @portfolio.portfolio_skills.includes(:assessor_override).to_a
      @vacancy.vacancy_skills.order(:id).map do |requirement|
        matches = skills.select { |skill| same_skill?(skill, requirement) }
        skill = matches.one? && matches.first.assessed? ? matches.first : nil
        candidate = skill && (skill.assessor_override&.override_level || skill.ai_level)
        delta = candidate && candidate - requirement.expected_level
        {
          skill_label: requirement.skill_label, skill_id: requirement.skill_id,
          expected_level: requirement.expected_level, candidate_level: candidate,
          delta: delta, result: delta.nil? ? 'not_assessed' : (delta.zero? ? 'match' : (delta.positive? ? 'exceed' : 'gap')),
          confidence: skill&.ai_confidence, is_override: !!skill&.assessor_override,
          assessment_reason: skill ? nil : (matches.size > 1 ? 'ambiguous_skill' : 'insufficient_evidence')
        }
      end
    end

    def same_skill?(skill, requirement)
      if requirement.skill_id.present? || skill.skill_id.present?
        requirement.skill_id.present? && skill.skill_id.present? &&
          requirement.skill_id.strip.casecmp?(skill.skill_id.strip)
      else
        normalize(requirement.skill_label) == normalize(skill.skill_label)
      end
    end

    def normalize(label)
      label.to_s.strip.downcase.gsub(/\s+/, ' ')
    end
  end
end
