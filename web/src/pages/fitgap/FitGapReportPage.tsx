import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import ComparisonTable from "@/components/fitgap/ComparisonTable";
import { sessionsApi } from "@/services/sessions";
import { portfoliosApi } from "@/services/portfolios";
import type { FitGapReport, Portfolio } from "@/types";

export default function FitGapReportPage() {
  const { id, sessionId, vacancyId } = useParams();
  const [report, setReport] = useState<FitGapReport | null>(null);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const response = await sessionsApi.getPortfolio(Number(sessionId));
      const value = 'portfolio' in response.data ? response.data.portfolio : null;
      if (!value || value.generation_status !== "complete") throw new Error("not ready");
      setPortfolio(value);
      const comparison = await portfoliosApi.getFitGap(value.id, Number(vacancyId));
      setReport(comparison.data.report);
    } catch { setError("The comparison could not be loaded. The assessment or role may be unavailable. Please retry."); }
    finally { setLoading(false); }
  }, [sessionId, vacancyId]);
  useEffect(() => { document.title = 'Role comparison | Rakamin AI Interview'; setReport(null); void load(); }, [load]);
  return <div className="review-workspace">
    <nav className="review-breadcrumb" aria-label="Assessment breadcrumb"><Link to={`/assessments/${id}/sessions/${sessionId}/portfolio`}>Evidence review</Link><span aria-hidden="true">/</span><span>Role comparison</span></nav>
    <header className="review-header"><div><p className="review-kicker">Fit / gap analysis</p><h1>Compare evidence, fairly.</h1><p className="text-muted-foreground mt-3">A skill gap and an unassessed skill require different next steps.</p></div>
      {report && portfolio && <Button disabled={busy} onClick={async () => {
        setBusy(true); setError("");
        try {
          const response = await portfoliosApi.exportPortfolio(portfolio.id, "pdf", Number(vacancyId));
          const url = URL.createObjectURL(new Blob([response.data as BlobPart], { type: "application/pdf" }));
          const link = document.createElement("a"); link.href = url; link.download = `comparison-${sessionId}.pdf`; link.click();
          setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch { setError("The PDF could not be downloaded. Please retry the export."); }
        finally { setBusy(false); }
      }}>{busy ? "Exporting..." : "Export comparison PDF"}</Button>}
    </header>
    {loading && <p role="status" className="review-state">Comparing assessed evidence with role requirements...</p>}
    {error && <div role="alert" className="review-error"><p>{error}</p><Button className="mt-3" variant="outline" onClick={() => void load()}>Retry comparison</Button></div>}
    {!loading && report && <><div className="review-caution mb-7">Unassessed means insufficient verified evidence, not a low rating. Review the transcript and collect a focused follow-up before a hiring decision.</div>
      <ComparisonTable comparisons={report.skill_comparisons} />
      <section className="review-state" aria-labelledby="comparison-summary"><h2 id="comparison-summary">Evidence summary</h2><p>{report.overall_narrative}</p><p>Culture fit cannot be inferred from skill scores. No automated hiring recommendation is made.</p></section>
    </>}
  </div>;
}
