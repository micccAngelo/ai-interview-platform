# Run with: bundle exec rails runner db/evidence_demo.rb
raise 'Synthetic demo seeds are development-only.' unless Rails.env.development?
org = Organization.find_or_create_by!(scheme: 'evidence-demo') do |record|
  record.name = 'Synthetic Evidence Demo'
  record.identifier = 'evidence-demo'
  record.host = 'evidence-demo.localhost'
end
Current.using(organization: org, tenant_id: org.id) do
  assessment = Assessment.find_or_create_by!(name: 'Synthetic evidence review') do |record|
    record.created_by = 9001
    record.time_limit_min = 30
  end
  definitions = [['react', 'React / Frontend Development'], ['communication', 'Communication'], ['system-design', 'System Design'], ['sql', 'Database Design & SQL']]
  definitions.each_with_index do |(id, label), index|
    assessment.assessment_skills.find_or_create_by!(skill_id: id) do |record|
      record.skill_label = label
      record.display_order = index
      record.expected_level = 3
      (1..5).each { |level| record.public_send("l#{level}_anchor=", "Synthetic rubric: level #{level} behavior.") }
    end
  end
  session = assessment.sessions.find_or_create_by!(candidate_name: 'Synthetic demo candidate') do |record|
    record.status = 'ended'
    record.started_at = 30.minutes.ago
    record.ended_at = Time.current
    record.duration_seconds = 1800
  end
  quotes = ['I split state by update frequency and measured the result with the React profiler.',
    'I wrote an incident update but relied on my lead to align stakeholders.']
  quotes.each_with_index do |quote, index|
    session.transcript_turns.find_or_create_by!(turn_number: index + 1) { |record| record.speaker = 'candidate'; record.text = quote }
  end
  definitions.each_with_index do |(id, label), index|
    session.coverage_maps.find_or_create_by!(skill_id: id) do |record|
      record.skill_label = label
      record.state = index.zero? ? 'covered' : (index == 1 ? 'initiated' : 'not_yet')
      record.probe_count = index.zero? ? 3 : (index == 1 ? 1 : 0)
    end
  end
  response = { 'configured_skills' => [
    { 'skill_id' => 'react', 'skill_label' => definitions[0][1], 'level' => 3, 'confidence' => 'high', 'evidence' => [quotes[0]], 'competency_summary' => 'Synthetic fixture: describes a measured approach to state isolation. The quote supports provenance; a human still needs to judge relevance and depth.' },
    { 'skill_id' => 'communication', 'skill_label' => definitions[1][1], 'level' => 2, 'confidence' => 'high', 'evidence' => [quotes[1]], 'competency_summary' => 'Synthetic fixture: describes communicating a status update with support from a lead. Interview coverage caps confidence at low.' }
  ], 'discovered_skills' => [] }
  client = Object.new
  client.define_singleton_method(:generate_content) { |*_args, **_options| response }
  portfolio = Portfolios::Generator.new(session: session, gemini_client: client).call
  vacancy = Vacancy.find_or_create_by!(role_title: 'Frontend Engineer / synthetic role') { |record| record.created_by = 9001 }
  definitions.each_with_index do |(id, label), index|
    vacancy.vacancy_skills.find_or_create_by!(skill_id: id) { |record| record.skill_label = label; record.expected_level = index == 3 ? 4 : 3 }
  end
  FitGap::Engine.new(portfolio: portfolio, vacancy: vacancy).call
  token = JsonWebToken.encode(user_id: 9001, role: 'admin', scheme: org.scheme)
  FileUtils.mkdir_p(Rails.root.join('tmp'))
  File.write(Rails.root.join('tmp/evidence-demo.json'), JSON.pretty_generate({ token: token, tenant: org.name,
    session_id: session.id, portfolio_id: portfolio.id, vacancy_id: vacancy.id,
    path: "/assessments/#{assessment.id}/sessions/#{session.id}/portfolio" }))
  puts 'Synthetic demo ready. Access details saved locally in api/tmp/evidence-demo.json (gitignored).'
end
