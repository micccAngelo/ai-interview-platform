# frozen_string_literal: true

Rails.application.config.filter_parameters += %i[
  password token authorization gemini_api_key assessor_notes candidate_name
  text evidence competency_summary
]
