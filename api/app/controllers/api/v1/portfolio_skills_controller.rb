# frozen_string_literal: true

module Api
  module V1
    class PortfolioSkillsController < ApiController
      authorize_auth_token! :assessor

      def override
        skill = PortfolioSkill.joins(portfolio: :session)
          .where(sessions: { tenant_id: current_tenant_id }).find(params[:id])
        portfolio = skill.portfolio
        result = nil
        portfolio.with_lock do
          skill.reload
          unless portfolio.complete? && skill.assessed?
            return json_error('Collect verified evidence before overriding this skill.', :unprocessable_entity)
          end
          result = skill.assessor_override || skill.build_assessor_override(ai_level: skill.ai_level)
          result.assign_attributes(params.require(:override).permit(:override_level, :assessor_notes))
          result.assign_attributes(overridden_by: current_user.id, overridden_at: Time.current)
          result.save!
          FitGapReport.where(portfolio_id: portfolio.id).delete_all
        end
        json_response(override: result.as_json(only: %i[id portfolio_skill_id ai_level override_level assessor_notes overridden_by overridden_at]))
      rescue ActiveRecord::RecordNotFound
        json_error('Portfolio skill not found', :not_found)
      rescue ActiveRecord::RecordInvalid => error
        json_error(error.record.errors.full_messages.first, :unprocessable_entity)
      end
    end
  end
end
