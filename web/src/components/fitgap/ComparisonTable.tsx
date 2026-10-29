import type { SkillComparison } from "@/types";
const labels = { match: "Meets requirement", exceed: "Above requirement", gap: "Below requirement", not_assessed: "Not assessed" };
export default function ComparisonTable({ comparisons }: { comparisons: SkillComparison[] }) {
  if (!comparisons.length) return <p role="status" className="review-state">This vacancy has no skill requirements. Add requirements before comparing.</p>;
  return <table className="comparison-table"><caption className="sr-only">Evidence compared with vacancy requirements</caption>
    <thead><tr><th scope="col">Skill</th><th scope="col">Required</th><th scope="col">Candidate</th><th scope="col">Comparison</th></tr></thead>
    <tbody>{comparisons.map((row, index) => <tr key={`${row.skill_label}-${index}`}>
      <th scope="row">{row.skill_label}</th><td>L{row.expected_level}</td>
      <td>{row.candidate_level == null ? "Unassessed" : `L${row.candidate_level}`}{row.is_override && <small>Reviewer override</small>}</td>
      <td>{labels[row.result]}{row.result === "not_assessed" ? <small>Collect follow-up evidence</small> : <small>{row.confidence} confidence in AI rating</small>}</td>
    </tr>)}</tbody>
  </table>;
}
