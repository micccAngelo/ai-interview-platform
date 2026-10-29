import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import SkillPortfolioCard from "@/components/portfolio/SkillPortfolioCard";
import { sessionsApi } from "@/services/sessions";
import { vacanciesApi } from "@/services/vacancies";
import { portfoliosApi } from "@/services/portfolios";
import { usePolling } from "@/hooks/usePolling";
import type { AssessorOverride, Portfolio, Vacancy } from "@/types";

export default function PortfolioPage() {
  const { id, sessionId } = useParams<{ id: string; sessionId: string }>();
  const navigate = useNavigate();
  const activeSession = useRef(sessionId);
  activeSession.current = sessionId;
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [busy, setBusy] = useState("");
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [vacancyError, setVacancyError] = useState(false);
  const [vacancy, setVacancy] = useState("");
  const [candidate, setCandidate] = useState("");
  const [filter, setFilter] = useState("all");
  const load = useCallback(async () => {
    try {
      const response = await sessionsApi.getPortfolio(Number(sessionId));
      if (activeSession.current !== sessionId) return;
      const data = response.data as { status?: string; portfolio?: Portfolio };
      if (!data.portfolio && data.status !== 'generating') throw new Error('Invalid portfolio response');
      setPortfolio(data.portfolio ?? null);
      setGenerating(data.status === "generating" || ["pending", "generating"].includes(data.portfolio?.generation_status ?? ""));
      setError("");
    } catch { if (activeSession.current === sessionId) { setError("We could not load the assessment. Check your connection and retry."); setGenerating(false); } }
    finally { if (activeSession.current === sessionId) setLoading(false); }
  }, [sessionId]);
  useEffect(() => {
    setPortfolio(null); setLoading(true); setFilter("all"); setActionError(""); setVacancy("");
    document.title = 'Evidence review | Rakamin AI Interview';
    void load();
    vacanciesApi.list().then((response) => { setVacancies(response.data.vacancies); setVacancyError(false); }).catch(() => setVacancyError(true));
    sessionsApi.get(Number(sessionId)).then((response) => setCandidate(response.data.session.candidate_name ?? "")).catch(() => setCandidate(""));
  }, [load, sessionId]);
  usePolling(load, 5000, generating);
  const skills = portfolio?.skills ?? [];
  const assessed = skills.filter((skill) => skill.assessment_status === "assessed").length;
  const followUp = skills.length - assessed;
  const visible = filter === "follow-up" ? skills.filter((skill) => skill.assessment_status !== "assessed") : skills;
  const complete = portfolio?.generation_status === "complete";
  const saveOverride = (value: AssessorOverride) => setPortfolio((current) => current && ({ ...current,
    overrides: [...current.overrides.filter((override) => override.portfolio_skill_id !== value.portfolio_skill_id), value],
  }));
  const exportFile = async (format: "pdf" | "json") => {
    if (!portfolio) return;
    setBusy(format); setActionError("");
    try {
      const response = await portfoliosApi.exportPortfolio(portfolio.id, format);
      const blob = new Blob([format === "json" ? JSON.stringify(response.data, null, 2) : response.data as BlobPart], { type: format === "json" ? "application/json" : "application/pdf" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a"); link.href = url; link.download = `portfolio-${sessionId}.${format}`;
      link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch { setActionError("The export could not be downloaded. Please retry."); }
    finally { setBusy(""); }
  };
  return <div className="review-workspace">
    <nav aria-label="Assessment breadcrumb" className="review-breadcrumb">
      <Link to="/assessments">Assessments</Link><span aria-hidden="true">/</span>
      <Link to={`/assessments/${id}/invite`}>Assessment sessions</Link><span aria-hidden="true">/</span><span>Evidence review</span>
    </nav>
    <header className="review-header">
      <div><p className="review-kicker">Interview portfolio</p><h1>Evidence before a decision.</h1>
        <p className="text-muted-foreground mt-3">{candidate ? `${candidate} / ` : ""}Session {sessionId}. Review what was demonstrated and what still needs a follow-up.</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <Button asChild variant="outline"><Link to={`/assessments/${id}/sessions/${sessionId}/transcript`}>Read transcript</Link></Button>
        {complete && <><Button variant="outline" onClick={() => exportFile("json")} disabled={!!busy}>Export JSON</Button><Button onClick={() => exportFile("pdf")} disabled={!!busy}>{busy === "pdf" ? "Exporting..." : "Export PDF"}</Button></>}
      </div>
    </header>
    {actionError && <p role="alert" className="review-error">{actionError}</p>}
    {loading && <div role="status" className="review-state">Loading candidate evidence...</div>}
    {error && <div role="alert" className="review-state"><h2>Assessment unavailable</h2><p>{error}</p><Button variant="outline" onClick={() => { setLoading(true); void load(); }}>Retry loading</Button></div>}
    {!loading && !error && generating && <div role="status" className="review-state"><h2>Checking the interview evidence</h2><p>This can take a few minutes. Ratings will appear after the complete response is validated.</p><Button variant="outline" onClick={() => void load()}>Check status</Button></div>}
    {!loading && !error && portfolio?.generation_status === "failed" && <div role="alert" className="review-state"><h2>Generation needs another attempt</h2><p>We could not complete this assessment. Existing evidence is preserved; no replacement ratings were published.</p><Button disabled={!!busy} onClick={async () => {
      setBusy("retry"); setActionError("");
      try { await sessionsApi.regeneratePortfolio(Number(sessionId)); await load(); }
      catch { setActionError("Generation could not be queued. Please retry in a moment."); }
      finally { setBusy(""); }
    }}>{busy === "retry" ? "Queuing..." : "Retry generation"}</Button></div>}
    {!loading && !error && complete && <>
      <section className="review-overview" aria-label="Evidence coverage">
        <div><span className="review-kicker">Evidence coverage</span><p><strong>{assessed}<span> / {skills.length}</span></strong> skills assessed</p></div>
        <div className="review-overview-note"><strong>{!skills.length ? "No skills returned" : followUp ? `${followUp} skill${followUp === 1 ? " needs" : "s need"} follow-up` : "Every skill has supporting evidence"}</strong><p>Missing evidence is not a low score. AI confidence describes interview signal, not candidate ability.</p></div>
      </section>
      <div className="review-body">
        <section className="min-w-0" aria-labelledby="skills-heading">
          <div className="review-section-header"><h2 id="skills-heading">Skill evidence</h2><div className="review-filters" role="group" aria-label="Filter skills">
            <button aria-pressed={filter === "all"} onClick={() => setFilter("all")}>All ({skills.length})</button>
            <button aria-pressed={filter === "follow-up"} onClick={() => setFilter("follow-up")}>Follow-up ({followUp})</button>
          </div></div>
          {visible.length === 0 && <div className="review-state"><h3>{skills.length ? "No follow-up skills in this view" : "No skills to review yet"}</h3><p>{skills.length ? "Choose All to read the assessment evidence." : "Add skills to the assessment and collect a new interview."}</p></div>}
          <div className="space-y-5">{visible.map((skill) => <SkillPortfolioCard key={skill.id} skill={skill} override={portfolio.overrides.find((override) => override.portfolio_skill_id === skill.id)} onOverrideSaved={saveOverride} />)}</div>
        </section>
        <aside className="review-sidebar" aria-labelledby="next-heading"><h2 id="next-heading">Continue the review</h2><p className="text-sm leading-6 text-muted-foreground">Compare the evidence against a role. Unassessed skills stay unassessed in the comparison.</p>
          <label htmlFor="vacancy" className="text-sm font-medium">Role to compare</label>
          <select id="vacancy" className="review-input w-full" value={vacancy} onChange={(event) => setVacancy(event.target.value)}><option value="">Choose a vacancy</option>{vacancies.map((item) => <option key={item.id} value={item.id}>{item.role_title}</option>)}</select>
          {vacancyError ? <p role="status" className="text-sm">Vacancies could not be loaded. Reload this page to retry.</p> : vacancies.length === 0 && <Link to="/vacancies/new" className="review-text-link">Create a vacancy</Link>}
          <Button className="w-full" disabled={!vacancy} onClick={() => navigate(`/assessments/${id}/sessions/${sessionId}/fitgap/${vacancy}`)}>Compare with role</Button>
          <div className="review-guidance"><h3>Before making a decision</h3><ol><li>Read evidence in its transcript context.</li><li>Probe missing or limited signal.</li><li>Record a reason for rating changes.</li></ol></div>
        </aside>
      </div>
    </>}
  </div>;
}
