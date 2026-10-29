# frozen_string_literal: true

class PreserveUnassessedPortfolioSkills < ActiveRecord::Migration[7.0]
  def up
    add_column :portfolio_skills, :assessment_status, :string, null: false, default: 'legacy'
    add_column :portfolio_skills, :assessment_reason, :string
    change_column_null :portfolio_skills, :ai_level, true
    add_check_constraint :portfolio_skills,
      "(assessment_status = 'not_assessed' AND ai_level IS NULL) OR " \
      "(assessment_status IN ('assessed', 'legacy') AND ai_level IS NOT NULL)",
      name: 'chk_portfolio_skills_assessment_status'
  end

  def down
    if select_value("SELECT COUNT(*) FROM portfolio_skills WHERE ai_level IS NULL").to_i.positive?
      raise ActiveRecord::IrreversibleMigration, 'Resolve unassessed rows before restoring NOT NULL; never invent ratings.'
    end

    remove_check_constraint :portfolio_skills, name: 'chk_portfolio_skills_assessment_status'
    change_column_null :portfolio_skills, :ai_level, false
    remove_column :portfolio_skills, :assessment_reason
    remove_column :portfolio_skills, :assessment_status
  end
end
