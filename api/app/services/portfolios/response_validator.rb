# frozen_string_literal: true

module Portfolios
  class ResponseValidator
    class InvalidResponse < StandardError; end

    CONFIDENCE = %w[low medium high].freeze

    def initialize(session:)
      @session = session
      @turns = session.transcript_turns.where(speaker: 'candidate').pluck(:text).map { |text| normalize(text) }
      @coverage = session.coverage_maps.to_a
    end

    def call(response)
      data = response.is_a?(String) ? JSON.parse(response) : response
      invalid! unless data.is_a?(Hash)
      configured = entries(data, 'configured_skills')
      discovered = entries(data, 'discovered_skills')
      definitions = @session.assessment.assessment_skills.order(:display_order).to_a
      known = definitions.map { |skill| key(skill) }
      invalid! unless configured.all? { |row| known.include?(key(row)) }
      discovered_maps = @coverage.select(&:is_discovered)
      invalid! unless discovered.all? { |row| row['skill_id'].to_s.empty? && discovered_maps.any? { |map| normalize(map.skill_label) == normalize(row['skill_label']) } }

      definitions.map do |definition|
        row = configured.find { |entry| key(entry) == key(definition) }
        build(definition, row, false)
      end + discovered.map do |row|
        definition = discovered_maps.find { |map| normalize(map.skill_label) == normalize(row['skill_label']) }
        build(definition, row, true)
      end
    rescue JSON::ParserError
      invalid!
    end

    private

    def entries(data, name)
      rows = data[name]
      invalid! unless rows.is_a?(Array) && rows.size <= 100 && rows.all? { |row| row.is_a?(Hash) && row['skill_label'].is_a?(String) }
      identities = rows.map { |row| key(row) }
      invalid! unless identities.uniq.size == identities.size
      rows
    end

    def build(definition, row, discovered)
      coverage = @coverage.find { |map| map.is_discovered == discovered && key(map) == key(definition) }
      base = { skill_id: discovered ? nil : definition.skill_id, skill_label: definition.skill_label, is_discovered: discovered }
      reason = if row.nil?
                 'omitted_by_model'
               elsif coverage.nil? || coverage.state == 'not_yet'
                 'not_explored'
               elsif !row['level'].is_a?(Integer) || !(1..5).cover?(row['level'])
                 'invalid_rating'
               elsif !CONFIDENCE.include?(row['confidence'])
                 'invalid_confidence'
               elsif !row['competency_summary'].is_a?(String) || row['competency_summary'].strip.empty? || row['competency_summary'].length > 6000
                 'invalid_summary'
               elsif !verified_evidence?(row['evidence'])
                 'unverified_evidence'
               end
      if reason
        return base.merge(ai_level: nil, ai_confidence: 'low', evidence: [],
          assessment_status: 'not_assessed', assessment_reason: reason,
          competency_summary: 'Insufficient verified evidence. Collect a follow-up assessment before assigning a level.')
      end

      ceiling = if coverage.state == 'covered' && coverage.probe_count >= 3
                  'high'
                elsif coverage.probe_count >= 2 || coverage.state == 'partial'
                  'medium'
                else
                  'low'
                end
      confidence = CONFIDENCE[[CONFIDENCE.index(ceiling), CONFIDENCE.index(row['confidence'])].min]
      base.merge(ai_level: row['level'], ai_confidence: confidence,
        evidence: row['evidence'].map(&:strip).uniq, competency_summary: row['competency_summary'].strip,
        assessment_status: 'assessed', assessment_reason: nil)
    end

    def verified_evidence?(quotes)
      quotes.is_a?(Array) && (1..3).cover?(quotes.size) && quotes.all? do |quote|
        quote.is_a?(String) && (12..3000).cover?(quote.strip.length) &&
          @turns.any? { |turn| turn.include?(normalize(quote)) }
      end
    end

    def key(value)
      id = value.is_a?(Hash) ? value['skill_id'] : value.skill_id
      label = value.is_a?(Hash) ? value['skill_label'] : value.skill_label
      id.to_s.strip.empty? ? "label:#{normalize(label)}" : "id:#{id.to_s.strip.downcase}"
    end

    def normalize(value)
      value.to_s.gsub(/\s+/, ' ').strip
    end

    def invalid!
      raise InvalidResponse, 'The model response did not match the assessment contract.'
    end
  end
end
