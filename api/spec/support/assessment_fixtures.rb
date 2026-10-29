module AssessmentFixtures
  QUOTE = 'I split state by update frequency and measured the result with the React profiler.'.freeze
  def domain
    @organization = Organization.create!(name: 'Synthetic Organization', scheme: "synthetic-#{SecureRandom.hex(4)}", identifier: SecureRandom.hex(4), host: 'example.test')
    @assessment = Assessment.unscoped.create!(tenant_id: @organization.id, created_by: 9001, name: 'Synthetic engineering assessment', time_limit_min: 30)
    @definitions = %w[React SQL].each_with_index.map do |label, index|
      anchors = (1..5).to_h { |level| ["l#{level}_anchor", "Synthetic level #{level} anchor"] }
      @assessment.assessment_skills.create!(anchors.merge(skill_id: label.downcase, skill_label: label, display_order: index, expected_level: 3))
    end
    @session = Session.unscoped.create!(tenant_id: @organization.id, assessment: @assessment, status: 'ended')
    @definitions.each_with_index do |skill, index|
      @session.coverage_maps.create!(skill_id: skill.skill_id, skill_label: skill.skill_label, state: index.zero? ? 'covered' : 'not_yet', probe_count: index.zero? ? 3 : 0)
    end
    @session.transcript_turns.create!(turn_number: 1, speaker: 'candidate', text: QUOTE)
    @session.transcript_turns.create!(turn_number: 2, speaker: 'ai', text: 'This sentence comes only from the interviewer and is not evidence.')
    @portfolio = @session.create_portfolio!(generation_status: 'pending')
    @vacancy = Vacancy.unscoped.create!(tenant_id: @organization.id, created_by: 9001, role_title: 'Synthetic frontend role')
    @vacancy.vacancy_skills.create!(skill_id: 'react', skill_label: 'React', expected_level: 3)
    @vacancy.vacancy_skills.create!(skill_id: 'sql', skill_label: 'SQL', expected_level: 4)
  end
  def payload
    { 'configured_skills' => [{ 'skill_id' => 'react', 'skill_label' => 'React', 'level' => 3,
      'confidence' => 'high', 'evidence' => [QUOTE], 'competency_summary' => 'Explains a measured state-management trade-off.' }], 'discovered_skills' => [] }
  end
  def generate(response = payload)
    client = double('model', generate_content: response)
    Portfolios::Generator.new(session: @session, gemini_client: client).call
  end
  def auth_headers(organization = @organization, role: 'admin')
    { 'Authorization' => "Bearer #{JsonWebToken.encode(user_id: 9001, role: role, scheme: organization.scheme)}" }
  end
end
