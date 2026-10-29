import type { AssessorOverride, PortfolioSkill } from "@/types";
import OverridePanel from "./OverridePanel";

const reasons: Record<string, string> = {
  omitted_by_model: "The model did not return an assessment for this skill.",
  not_explored: "This skill was not explored in the interview.",
  invalid_rating: "The model returned an invalid or missing rating.",
  invalid_confidence: "The model returned an invalid confidence value.",
  invalid_summary: "The model did not return a usable explanation.",
  unverified_evidence: "Supporting excerpts could not be verified against candidate turns.",
};

export default function SkillPortfolioCard({ skill, override, onOverrideSaved }: {
  skill: PortfolioSkill; override?: AssessorOverride; onOverrideSaved: (value: AssessorOverride) => void;
}) {
  const assessed = skill.assessment_status === "assessed" && skill.ai_level !== null;
  const legacy = skill.assessment_status === "legacy";
  return <article className="review-skill" aria-labelledby={`skill-${skill.id}`}>
    <div className="review-skill-heading">
      <div className={assessed ? "review-level" : "review-level review-level-missing"}>
        {assessed ? <><span>Level</span><strong>{override?.override_level ?? skill.ai_level}</strong></> : <strong>?</strong>}
      </div>
      <div className="min-w-0 flex-1">
        <h3 id={`skill-${skill.id}`} className="text-lg font-semibold break-words">{skill.skill_label}</h3>
        <p className="text-sm text-muted-foreground mt-1">
          {assessed ? `${skill.ai_confidence} confidence in AI rating` : legacy ? "Legacy rating: evidence not verified" : "Not assessed"}
          {skill.is_discovered && " / Discovered in interview"}
        </p>
        {override && <p className="review-attribution">Reviewer override: L{override.override_level} / Original AI: L{override.ai_level}</p>}
      </div>
      <span className={assessed ? "review-status" : "review-status review-status-warning"}>{assessed ? "Evidence available" : "Follow-up needed"}</span>
    </div>
    {assessed ? <>
      <p className="text-sm leading-7 break-words">{skill.competency_summary}</p>
      {skill.ai_confidence === "low" && <p className="review-caution">Limited interview signal. Probe this skill further if it is important for the role.</p>}
      <details className="review-evidence" open>
        <summary>Candidate evidence ({skill.evidence.length})</summary>
        <p className="text-xs text-muted-foreground mt-3">Excerpts matched to candidate transcript turns. Assess relevance and context before deciding.</p>
        {skill.evidence.map((quote, index) => <blockquote key={index} className="review-quote">{quote}</blockquote>)}
      </details>
    </> : <div className="review-caution">
      <p className="font-medium">{legacy ? "This rating predates evidence verification." : reasons[skill.assessment_reason ?? ""] ?? "There is not enough verified evidence to assign a level."}</p>
      <p className="mt-1">Collect a focused follow-up assessment. Missing evidence is not a low score.</p>
    </div>}
    {override && <div className="review-note" role="status"><strong>Saved reviewer rationale</strong><p className="mt-1 whitespace-pre-wrap break-words">{override.assessor_notes}</p></div>}
    <OverridePanel skill={skill} existingOverride={override} onSaved={onOverrideSaved} />
  </article>;
}
