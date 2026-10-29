import type { Portfolio } from '../src/types';
export const portfolio: Portfolio = {
  id: 1, session_id: 1, generation_status: 'complete', overrides: [],
  skills: [
    { id: 1, skill_id: 'react', skill_label: 'React / Frontend Development', is_discovered: false,
      ai_level: 3, ai_confidence: 'high', assessment_status: 'assessed',
      evidence: ['I split state by update frequency and measured the result with the React profiler.'],
      competency_summary: 'Describes a measured approach to state isolation. Probe how the approach behaves with concurrent requests.' },
    { id: 2, skill_id: 'sql', skill_label: 'Database Design & SQL', is_discovered: false,
      ai_level: null, ai_confidence: 'low', assessment_status: 'not_assessed', assessment_reason: 'not_explored', evidence: [],
      competency_summary: 'Insufficient verified evidence.' },
  ],
};
