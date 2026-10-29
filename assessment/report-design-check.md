# PDF design and copy review: PASS

Scope: the revised submission report. Application screens, test results and the walkthrough are unchanged. `report-checks.json` records the final PDF hash and the automated checks.

Design read: a technical report for a recruiter and engineering reviewer. Georgia supports sustained reading; Calibri keeps tables compact; Consolas distinguishes commands and commit IDs. Charcoal identifies table headers and muted rust marks section numbers and source links. ENERGY 1 / RHYTHM 2 / MOTION 1. The static document uses no animation.

## Hard gate

- R-02 PASS: extracted report text contains no em dash, en dash or nonbreaking hyphen. Slogan-style headings were replaced with factual section names.
- R-03 PASS: all extracted characters lie within page bounds. All ten pages were inspected individually after Poppler rendering; tables, captions and phone figures fit.
- R-17 PASS: the report retains 47 backend examples, 11 component tests, 3 browser workflows and 9 live control checks from the existing verification record.
- R-18 PASS: no testimonial or endorsement appears.
- R-23 PASS: existing application screenshots are retained. No invented logo, person, metric or illustration was added.
- R-24 PASS: four PDF URI annotations retain the existing primary-source destinations. The contents list refers to the actual pages 2-10.
- R-25 PASS: all seven authored text/background combinations exceed 4.5:1; the minimum is 5.78:1. Screenshot contrast evidence remains in the separate application review.
- R-26 PASS: source references are actual PDF links. No decorative object is styled as a button or form.
- R-27 PASS: data-state requirements apply to the application, whose existing verification is unchanged. The report identifies the illustrated failed save and the recovery test.
- R-28 PASS: no FAQ was added.
- R-32 PASS: the fixed PDF adds no keyboard-dependent interface. It preserves selectable text and standard link annotations; application keyboard checks remain documented separately.
- R-33 PASS: layout and copy are authored in `scripts/build-report.py`; no application source or stylesheet was patched by the report generator.
- R-34 PASS: no theme toggle exists in the report.
- R-35 PASS: ReportLab generation succeeded, the PDF reopened with pypdf and pdfplumber, and every final page was rendered and inspected.
- R-36 PASS: test counts, limitations and the AI-assistance disclosure remain accurate. The report adds no claimed research, certification or performance improvement.
- R-37 PASS: the user requested a visual and copy revision. The document has a stated audience, typography, palette and dials.
- R-38 PASS: synthetic demonstration content remains identified; no account of personal research or user interviews was invented.
- R-39 PASS: headings, body copy, tables, captions and references have consistent reading roles. HTML control, focus and landmark requirements do not apply to this fixed PDF. PDF accessibility certification is not claimed.
- R-40 PASS: every embedded screenshot has an explicit draw width and height. The report loads no external font, media or script and gives no unmeasured performance number.

## Purpose gate

- R-01 PASS: no gradients or glow treatments appear.
- R-04 PASS: the report adds no decorative icons; original product navigation icons remain inside labelled screenshots.
- R-06 PASS: the serif/sans pairing separates prose from reference tables; monospace is limited to commands and commit IDs. No wide-tracked uppercase labels are used.
- R-07 PASS: no background grid or dot pattern appears.
- R-08 PASS: no decorative arrows appear in report copy.
- R-09 PASS: no promotional badges or pills appear.
- R-10 PASS: no glass effect appears.
- R-12 PASS: rules and row shading separate content without large shadows.
- R-13 PASS: no glow appears.
- R-14 PASS: repeated table rows compare the same kind of information; prose, screenshots, commands and the contents list use different structures.
- R-19 PASS: the motion dial is consistent with a static document.
- R-22 PASS: no generic illustration appears.

## Liveliness and craftsmanship

- Dials PASS: quiet typography, varied page structures and static content match ENERGY 1 / RHYTHM 2 / MOTION 1.
- Focal point PASS: the cover names the technical problem; each later page has a specific section heading.
- Whitespace PASS: section gaps separate findings, decisions and evidence; table padding groups related text.
- Accent PASS: muted rust consistently marks the section rail, table-header rules and source links.
- Identity PASS: the section rail and serif headings repeat across the report; the cover uses the actual SQL rating problem rather than a slogan.
- Design Read PASS: audience and visual choices were set before authoring and described in the progress update.
- C-1 PASS: type, color and spacing each have a stated reading purpose.
- C-2 PASS: PDF references use real URI annotations; there are no simulated controls.
- C-3 PASS: the assignment requirements determine the sections; no marketing filler section was added.
- C-4 PASS: all ten pages have readable, unclipped content in the final renders.
- C-5 PASS: the report retains the recorded test evidence and limits without inventing outcomes.
- R-05 PASS: page structure follows setup, findings, criteria, implementation and verification rather than a marketing template.
- R-11 PASS: rules, rectangular tables and plain text provide grouping; the report adds no pills.
- R-15 PASS: source links and submission labels identify their actual destinations and status.
- R-16 PASS: generic promotional wording was replaced with code behavior, field names and observed failures.
- R-20 PASS: the SQL example, migration behavior and rollback correction identify the actual project work.
- R-21 PASS: white paper with dark ink is an explicit reading choice; no theme request was deferred.
- R-29 PASS: charcoal and muted rust form the palette, with neutral paper and rules.
- R-30 PASS: the revision uses the report's own section rail and type pairing; it does not recreate a referenced third-party design.
- R-31 PASS: each major layout decision has a specific readability or navigation purpose above.

## Copy review

- Facts PASS: the rewrite adds no new interview, person, testimonial or result. The previously recorded 9 control checks now appear in the verification summary.
- Voice PASS: the report uses direct technical prose. Original slogan headings such as “Tests must catch a wrong result” and “Prioritize candidate harm” are removed.
- Rhythm PASS: headings name subjects; paragraphs describe behavior and corrections without a repeated slogan or forced conclusion.
- Clarity PASS: the rewrite shortens repeated caveats while retaining the distinctions between local tests, live model quality, legal compliance and external submission.
- Attribution PASS: AI assistance and synthetic data remain disclosed.

The application checks remain in `design-verification.md`. This report revision did not require rerunning application tests because it changes only report generation and delivery documentation.
