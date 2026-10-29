import { useState } from "react";
import type { AssessorOverride, PortfolioSkill } from "@/types";
import { portfoliosApi } from "@/services/portfolios";
import { Button } from "@/components/ui/button";

export default function OverridePanel({ skill, existingOverride, onSaved }: {
  skill: PortfolioSkill; existingOverride?: AssessorOverride; onSaved: (value: AssessorOverride) => void;
}) {
  const [level, setLevel] = useState(existingOverride?.override_level ?? skill.ai_level ?? 1);
  const [notes, setNotes] = useState(existingOverride?.assessor_notes ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  if (skill.assessment_status !== "assessed") return null;

  return <details className="review-override" onKeyDown={(event) => {
    if (event.key === "Escape") { event.currentTarget.open = false; event.currentTarget.querySelector("summary")?.focus(); }
  }}>
    <summary>{existingOverride ? "Edit reviewer override" : "Review or override rating"}</summary>
    <form className="space-y-4 pt-4" onSubmit={async (event) => {
      event.preventDefault(); setSaving(true); setError("");
      try {
        const response = await portfoliosApi.getOverride(skill.id, { override_level: level, assessor_notes: notes.trim() });
        onSaved(response.data.override);
      } catch { setError("The override was not saved. Your notes are still here. Please retry."); }
      finally { setSaving(false); }
    }}>
      <p className="text-sm text-muted-foreground">Review the excerpt and its context first. The original AI rating remains in the record.</p>
      <div className="space-y-2">
        <label className="block text-sm font-medium" htmlFor={`rating-${skill.id}`}>Reviewer level</label>
        <select id={`rating-${skill.id}`} className="review-input" value={level} onChange={(event) => setLevel(Number(event.target.value))} disabled={saving}>
          {[1, 2, 3, 4, 5].map((value) => <option key={value} value={value}>Level {value}</option>)}
        </select>
      </div>
      <div className="space-y-2">
        <label className="block text-sm font-medium" htmlFor={`notes-${skill.id}`}>Reason for this rating <span className="text-muted-foreground">(required)</span></label>
        <textarea id={`notes-${skill.id}`} className="review-input min-h-28" required maxLength={4000} value={notes} onChange={(event) => setNotes(event.target.value)} disabled={saving} />
      </div>
      {error && <p role="alert" className="review-error">{error}</p>}
      <Button type="submit" disabled={saving || !notes.trim()}>{saving ? "Saving override..." : "Save reviewer override"}</Button>
    </form>
  </details>;
}
