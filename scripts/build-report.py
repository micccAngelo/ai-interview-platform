from pathlib import Path
import json
from html import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assessment'
proof = json.loads((OUT / 'verification.json').read_text(encoding='utf-8-sig'))
for name, filename in [('BodyFont', 'segoeui.ttf'), ('BoldFont', 'segoeuib.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / filename)))
pdfmetrics.registerFontFamily('BodyFont', normal='BodyFont', bold='BoldFont')
INK = colors.HexColor('#142f37')
TEAL = colors.HexColor('#075f68')
MUTED = colors.HexColor('#50616a')
PALE = colors.HexColor('#eff7f7')
YELLOW = colors.HexColor('#fff4d7')
LINE = colors.HexColor('#c6d6d9')
W = A4[0] - 96
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Text', fontName='BodyFont', fontSize=10, leading=15, textColor=INK, spaceAfter=9))
styles.add(ParagraphStyle(name='SmallText', parent=styles['Text'], fontSize=8.3, leading=12, textColor=MUTED, spaceAfter=6))
styles.add(ParagraphStyle(name='SectionTitle', fontName='BoldFont', fontSize=23, leading=29, textColor=INK, spaceAfter=16))
styles.add(ParagraphStyle(name='SubTitle', fontName='BoldFont', fontSize=12, leading=17, textColor=TEAL, spaceBefore=9, spaceAfter=9))
styles.add(ParagraphStyle(name='Kicker', fontName='BoldFont', fontSize=9, leading=13, textColor=TEAL, spaceAfter=8))
styles.add(ParagraphStyle(name='CoverTitle', fontName='BoldFont', fontSize=39, leading=43, textColor=INK, spaceAfter=20))
styles.add(ParagraphStyle(name='Cell', parent=styles['Text'], fontSize=8.2, leading=12, spaceAfter=0))
styles.add(ParagraphStyle(name='CellHead', parent=styles['Cell'], fontName='BoldFont', textColor=TEAL))
story = []
def p(text, style='Text'):
    return Paragraph(text, styles[style])
def add(text, style='Text'):
    story.append(p(text, style))
def title(step, text):
    add(step, 'Kicker'); add(text, 'SectionTitle')
def sub(text): add(text, 'SubTitle')
def table(headers, rows, widths):
    data = [[p(escape(str(value)), 'CellHead') for value in headers]] + [[p(escape(str(value)), 'Cell') for value in row] for row in rows]
    item = Table(data, colWidths=[W * width for width in widths], repeatRows=1, hAlign='LEFT')
    item.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),.5,LINE)]))
    story.append(item); story.append(Spacer(1,12))
def box(text):
    item = Table([[p(text)]], colWidths=[W]); item.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),YELLOW),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#d9c28b')),('LEFTPADDING',(0,0),(-1,-1),15),('RIGHTPADDING',(0,0),(-1,-1),15),('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),8)])); story.append(item); story.append(Spacer(1,14))
def screenshot(name, max_height=510, width=W):
    file = OUT / 'screenshots' / name
    if not file.exists(): raise FileNotFoundError(file)
    image = Image(str(file)); ratio = min(width/image.imageWidth, max_height/image.imageHeight)
    image.drawWidth = image.imageWidth * ratio; image.drawHeight = image.imageHeight * ratio
    image.hAlign='LEFT'; story.append(image); story.append(Spacer(1,9))
def newpage(): story.append(PageBreak())
def footer(canvas, doc):
    canvas.saveState(); canvas.setStrokeColor(LINE); canvas.line(48,44,A4[0]-48,44)
    canvas.setFont('BodyFont',8); canvas.setFillColor(MUTED)
    canvas.drawString(48,30,'Rakamin / Product Engineer case study / 30 October 2026')
    canvas.drawRightString(A4[0]-48,30,str(doc.page))
    if doc.page > 1:
        canvas.setFillColor(TEAL); canvas.setFont('BoldFont',8)
        canvas.drawString(48,A4[1]-32,'Evidence before a decision')
    canvas.restoreState()

story.append(Spacer(1,25))
add('Fullstack Product Engineer / Case study', 'Kicker')
add('Evidence before<br/>a decision.', 'CoverTitle')
add('A complete assessment review slice for the AI Interview Platform. Missing evidence stays unassessed, validated results publish atomically, and reviewers can see what supports each rating.')
story.append(Spacer(1,14))
box('<b>The product decision</b><br/>An interview that did not assess SQL should not give a candidate L1 in SQL. The system must preserve that uncertainty through storage, human review, role comparison and export.')
table(['Delivered locally', 'Verification evidence'], [
    ['Rails data boundary and persistence', f"{proof['backend_examples']} backend examples passed against PostgreSQL."],
    ['React evidence workspace', f"{proof['frontend_tests']} component tests and {proof['browser_tests']} browser workflow tests passed; production build passed."],
    ['Submission materials', 'This report, screenshots, captioned walkthrough, source, runbook, test logs and technical defense notes.'],
], [.46,.54])
sub('Publication status')
add('Kept entirely in Rakamin2 at the user\'s request. No GitHub publication, external video hosting or portal submission was performed.', 'SmallText')
add(('Pull request: <a href="'+escape(proof['pr_url'],quote=True)+'">Open pull request</a>') if proof.get('pr_url') else 'Pull request: not published. A reviewable local feature branch and PR description are included.', 'SmallText')
add(('Video: <a href="'+escape(proof['video_url'],quote=True)+'">Hosted demonstration</a>') if proof.get('video_url') else f"Video: local walkthrough.webm is included ({proof['video_duration_seconds']:.0f} seconds, captioned).", 'SmallText')
add('Prepared with AI assistance. All demonstration records are explicitly synthetic. The included technical-defense guide is intended to support the candidate\'s own review and understanding.', 'SmallText')

newpage(); title('Step 1 / Setup and local exploration', 'Start with the real system.')
add('The supplied repository was cloned into Rakamin2. Main is preserved at baseline b836d02; implementation lives on feat/evidence-first-assessment. No other candidates\' pull requests or solutions were used.')
table(['Layer', 'Baseline and local verification'], [
    ['API', 'Ruby 3.3.2, Rails 7.0, PostgreSQL. Original RSpec suite had no feature specs. Portable local tooling was needed on this Windows host.'],
    ['Web', 'React 18, TypeScript, Vite, Tailwind and Radix primitives. Added a lockfile, Vitest/Testing Library and Playwright.'],
    ['Workflow inspected', 'Assessment setup, session, portfolio generation, evidence review, override, vacancy comparison and export. Code paths were traced before changes; the implemented review slice was exercised in a browser.'],
    ['Real database', 'PostgreSQL runs on localhost:54329 with a dedicated local cluster. Tests inspect actual persisted status, levels, evidence and rollback behavior.'],
    ['Model dependency', 'Deterministic injected responses exercise the real validator and persistence pipeline. No live Gemini or microphone interview was performed.'],
], [.24,.76])
sub('Reproducible checks')
add('API: bundle exec rails db:prepare; bundle exec rspec --format documentation.<br/>Web: npm ci; npm test; npm run build; npm run test:e2e.<br/>The repository includes CI configuration. Local results are recorded separately from CI, which is not claimed to have run on GitHub.', 'SmallText')
sub('Scope and environment constraints')
add('The slice begins with a completed interview and ends with a human-readable role comparison and export. Live audio capture, interview quality and upstream identity integration remain outside the proven behavior. Docker was unavailable locally; the alternative compose setup is supplied but not described as tested.')
add('The brief lists Wednesday 19 August, 13:00 WIB. This work was prepared on 29-30 October 2026. The older deadline is recorded as supplied context, with no assumption of an extension.', 'SmallText')

newpage(); title('Step 2 / Deep context and domain immersion', 'Design for the person being assessed.')
add('The product specification emphasizes probing real capability and using transcript evidence. Its simulation connects portfolio review, assessor overrides and vacancy comparison. [1, 2] That makes trustworthy interpretation of evidence the most useful bounded improvement.')
add('The user jobs below are working hypotheses derived from the brief and product flow. They are not claims of interviews or field research with Indonesian recruiters.', 'SmallText')
table(['Person', 'Working condition and product implication'], [
    ['Assessor', 'Needs to read excerpts in context and correct a rating with a reason. Put provenance before the override control.'],
    ['Recruiter', 'Needs to see what remains unknown before sharing results. Show explicit follow-up counts and preserve them in exports.'],
    ['Hiring manager', 'Needs a comparison against actual role requirements. Separate demonstrated gaps from requirements the interview did not assess.'],
    ['Candidate', 'Did not choose the scoring system and bears the cost of a wrong interpretation. Never convert missing signal into a negative score or an unsupported hiring recommendation.'],
], [.24,.76])
sub('Indonesia and UU PDP implications')
add('UU 27/2022 provides rights concerning correction and access (Articles 6-7), objection to certain solely automated decisions (Article 10), and impact assessment for high-risk processing (Article 34). It also addresses purpose, accuracy and confidentiality. [3]')
add('Engineering interpretation: keep human review meaningful, minimize provider inputs, preserve uncertainty, bind evidence access to a tenant, and avoid raw provider errors in logs or responses. These safeguards support a privacy program; they do not establish legal compliance.')
box('<b>Escalate before real hiring use</b><br/>The controller must settle legal basis, retention, deletion and correction operations, candidate objection handling, cross-border/provider arrangements and any required impact assessment. Model quality, language effects and fairness still need evaluation with consented data.')

newpage(); title('Step 3 / Problem and gap analysis', 'Prioritize candidate harm.')
table(['Priority / kind', 'Observed gap and workflow impact', 'Disposition'], [
    ['P0 / defect', 'Portfolio and override lookups did not join through the authenticated tenant. Foreign IDs could expose or change candidate evidence.', 'Tenant-bound lookup and request tests.'],
    ['P0 / missing policy', 'Local password login could select an organization without a user-membership relation. This cannot establish tenant authorization.', 'Opt-in development-only login; verify token tenant binding. Upstream identity policy remains a dependency.'],
    ['P1 / defect', 'to_i.clamp(1,5) turned malformed or missing model ratings into valid-looking levels.', 'Strict types and explicit not_assessed status.'],
    ['P1 / defect', 'Old skills were deleted before all replacement rows were validated or persisted.', 'Validate first; publish inside a savepoint.'],
    ['P1 / defect', 'Duplicate work could regenerate results; an exhausted older job could mark a completed portfolio failed.', 'Session lock, completed-work skip and guarded exhaustion callback.'],
    ['P1 / missing specification', 'Quote provenance, unassessed-state semantics and confidence ceilings were undefined.', 'Self-defined acceptance criteria and validator.'],
    ['P1 / unsafe inference', 'The fit/gap prompt requested culture fit and hiring recommendations from score patterns.', 'Deterministic comparison; no inferred culture or automated recommendation.'],
    ['P2 / seam defect', 'API expected_level was read as required_level in the UI.', 'Shared typed contract and regression test.'],
    ['P2 / defect', 'Some request errors were swallowed; responsive headings and enlarged text failed browser checks.', 'Visible retry states; mobile grid and wrapping navigation.'],
    ['P3 / documentation', 'Setup examples used an inconsistent API port and frontend folder name.', 'Correct defaults; add a verified runbook.'],
], [.17,.60,.23])
add('P0 is a blocker for candidate data access; P1 can materially distort an assessment or lose evidence; P2 interrupts correct interpretation or recovery; P3 slows setup. Priorities express impact, not measured incident frequency.', 'SmallText')

newpage(); title('Step 4 / Acceptance criteria', 'Define correct behavior first.')
add('The acceptance criteria were written and committed before implementation commits. The full checklist is in acceptance-criteria.md. Each item below has an observable failure condition.')
table(['Boundary', 'Correct behavior and important edge cases'], [
    ['Rating types', 'Only integer 1..5. Null, strings, floats, booleans, 0 and 6 do not become ratings.'],
    ['Completeness', 'Every configured skill is represented. An omitted or untouched skill is explicitly unassessed.'],
    ['Provenance', '1-3 bounded excerpts must occur in candidate turns after whitespace normalization. AI-only and invented quotes cannot justify a score.'],
    ['Confidence', 'Known confidence values only, bounded by coverage state and probe count. Confidence describes signal, not candidate ability.'],
    ['Malformed response', 'Unknown or duplicate identities and wrong JSON shapes fail the attempt without replacing old rows.'],
    ['Atomic publication', 'All rows and completion status commit together. A later validation or DB failure restores the previous rows.'],
    ['Jobs and recovery', 'Duplicate jobs serialize; complete work is skipped. Queue failure leaves a failed portfolio retryable. Exhaustion cannot clobber complete work.'],
    ['Historical data', 'Old ratings are labelled legacy. No existing row silently gains verified provenance. Schema rollback refuses to invent levels for null rows.'],
    ['Human override', 'Only assessed evidence can be overridden. Require a bounded rationale and retain original AI level plus reviewer attribution.'],
    ['Authorization', 'Foreign tenant resource IDs return 404. Candidate roles cannot read assessor evidence. Background comparison checks both tenants.'],
    ['Comparison', 'Use expected_level. Never match different canonical IDs by label; ambiguous custom matches remain unassessed.'],
    ['Interface', 'Loading, empty, request error, failed generation, partial, legacy and long-text states; keyboard focus, phone layout and 200% text size.'],
], [.24,.76])

newpage(); title('Step 4 / Strategy and trade-offs', 'Choose a smaller correctness boundary.')
table(['Option', 'Impact / cost', 'Maintainability and failure mode'], [
    ['A. UI warning', 'Low cost; helps a reviewer notice uncertainty.', 'Leaves fabricated scores and destructive writes intact. API/export consumers remain exposed. Rejected.'],
    ['B. Strict evidence boundary + atomic publication', 'Moderate schema and test work; protects the complete review slice.', 'Chosen. Simple services and no new infrastructure. Conservative quote matching rejects paraphrases; a bounded model call holds a DB connection and session row lock.'],
    ['C. Versioned ledger + outbox + evaluation service', 'Best long-term history, durable scheduling and evaluation separation; much larger implementation.', 'More operational ownership and migration cost. A sensible next stage after validating scoring policy, not a prerequisite to fix score coercion.'],
], [.22,.32,.46])
sub('The implemented data path')
table(['1. Interview', '2. Boundary', '3. Publication', '4. Review', '5. Comparison'], [['Ended session and candidate transcript', 'Strict response shape, provenance and confidence', 'Validated rows and completion in one transaction', 'Evidence, follow-up and attributed override', 'Rule-based role requirements and export']], [.2,.2,.2,.2,.2])
sub('Migration and rollback')
add('Add assessment_status (default legacy) and assessment_reason. Make ai_level nullable. A database check requires null exactly for not_assessed and a level for assessed or legacy. Old scores remain intact; they are not retroactively called verified.')
add('The migration round-trip is tested on legacy rows. Down refuses while null ratings exist, rather than deleting evidence or inventing scores. For an application rollback, retain the additive schema; reconcile or archive unassessed records before reverting the schema.')
sub('Failure boundaries')
add('The portfolio call uses a 180-second HTTP read timeout and disables provider retries; Sidekiq owns durable retries. This is not a strict end-to-end wall-clock deadline. Publication is serialized per session. Exactly-once provider billing, crash watchdogs, an outbox, append-only reviewer history and fairness calibration are not delivered guarantees.', 'SmallText')

newpage(); title('Step 5 / Implementation and correctness proof', 'Tests must catch a wrong result.')
table(['Check', 'Recorded outcome'], [
    ['Backend', f"{proof['backend_examples']} passing examples; real PostgreSQL persistence, response validation, tenant requests, rollback, worker exhaustion and concurrent duplicate jobs."],
    ['Frontend', f"{proof['frontend_tests']} passing component tests; {proof['browser_tests']} passing browser workflow tests; TypeScript and production build pass."],
    ['Live API seam', proof.get('live_api_summary', 'See verification.json for the separately recorded live API check.')],
    ['Seeded fault', 'A missing score was deliberately changed into L1 on a scratch branch. The strict missing-rating test failed, then the fault was reverted. Assertions were not weakened.'],
], [.26,.74])
fault = proof['seeded_fault']
add('Seeded-fault history', 'SubTitle')
add(f"Scratch branch: {escape(fault['branch'])}<br/>Fault commit: {escape(fault['mutant'])}<br/>Revert commit: {escape(fault['revert'])}<br/>Observed result: {escape(fault['result'])}", 'SmallText')
sub('AI verification moment')
add('An initially generated savepoint implementation was still unsafe: Rails retained rolled-back association targets and autosaved a new skill while storing failure status. The PostgreSQL rollback test expected only the original row and observed an extra row. Reloading the portfolio clears those targets before the failure update. The original failed output is retained in ai-verification-red.log; the assertion was unchanged.')
add('The first generated UI called a regeneration method that did not exist and treated a union response as if it always held a portfolio. TypeScript rejected both. The calls were corrected against the existing session API and the build passed.')
add('Browser checks then caught skill headings squeezed by a status label on phones and navigation overflow at 200% text size. The layout was changed to an explicit mobile grid and wrapping navigation; the original overflow assertion remained unchanged and passed.')
box('<b>Evidence is bounded</b><br/>A quote occurrence check establishes provenance. It does not establish semantic relevance, proficiency, model calibration or absence of bias. Synthetic test success is not a validation of hiring outcomes.')

newpage(); title('Step 5 / Interface evidence', 'Make missing signal visible.')
add('Desktop evidence review. Synthetic browser fixtures; counts and states are derived from the fixture API payload. The latest screenshots were taken after the responsive fixes.', 'SmallText')
screenshot('01-review-desktop.png', 470)
add('Coverage appears before individual ratings. Evidence and its provenance note appear before the reviewer action. A side panel keeps role comparison available without replacing the evidence context.', 'SmallText')
sub('Design decisions')
add('Extend the existing teal/yellow identity. Darker teal improves primary-button contrast; yellow denotes follow-up. System sans supports dense reading. Native disclosure controls keep excerpts and reviewer forms keyboard accessible. ENERGY 1 / RHYTHM 2 / MOTION 1.', 'SmallText')

newpage(); title('Step 5 / Responsive and failure states', 'Recovery is part of the workflow.')
add('Phone review and a failed override save are exercised in the browser suite. The failure is deliberately simulated, and the rationale remains available for retry.', 'SmallText')
phone_images = []
for name in ['08b-mobile-overview.png', '08c-mobile-evidence.png']:
    item = Image(str(OUT / 'screenshots' / name))
    scale = min((W*.45)/item.imageWidth, 450/item.imageHeight)
    item.drawWidth = item.imageWidth*scale; item.drawHeight = item.imageHeight*scale
    phone_images.append(item)
phones = Table([phone_images], colWidths=[W*.5,W*.5]); phones.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0)])); story.append(phones)
add('Phone overview and evidence detail. The full phone capture is included at native resolution. The browser test also enlarges text to 200% and checks for horizontal overflow.', 'SmallText')
screenshot('02b-save-error-message.png', 55)
add('Other included captures: role comparison, request retry, empty results, pending generation and failed generation. No control silently claims a failed save or export succeeded.', 'SmallText')

newpage(); title('Step 6 / Handoff and release boundaries', 'Review locally, then publish deliberately.')
sub('Included in Rakamin2')
add('Source changes in api/ and web/; local Git feature branch and seeded-fault history; assessment test logs and verification.json; screenshots; sample JSON/PDF exports; walkthrough.webm; RUNBOOK.md; technical-defense.md; PR_DESCRIPTION.md; source archive and Git bundle.')
sub('Before external submission')
add('Publish the feature branch and open the prepared pull request against rakamindev/ai-interview-platform. Host the captioned 3-5 minute walkthrough on the chosen external platform. Replace the publication status at the front of this report with the resulting URLs, then upload the single PDF in the hiring portal. No portal submission is claimed here.')
sub('Operational rollout')
add('Apply the additive migration first, then deploy API and web together so nullable ratings and assessment statuses are understood by all consumers. Review legacy records and plan follow-up assessments. Monitor generation failures, pending-job age, provider latency, missing-evidence rates and assessor overrides before expanding use. No target rates or performance claims are invented.')
sub('Known limits')
add('Live Gemini and audio are unverified. Historical complete portfolios require follow-up rather than automatic verification. The latest override is retained, not a full review ledger. A row lock spans the model call. There is no durable outbox or abandoned-job watchdog. Upstream organization identity and the controller\'s privacy policies remain dependencies. PDF font coverage beyond Latin is not validated.')
sub('Primary sources')
refs = [
 ('1. Product behavior specification', 'https://github.com/rakamindev/ai-interview-platform/wiki/PRD-01-%E2%80%94-First-Principles:-AI-Interview-Behavior'),
 ('2. Product workflow simulation', 'https://github.com/rakamindev/ai-interview-platform/wiki/PRD-02-%E2%80%94-Real-Simulation:-End%E2%80%90to%E2%80%90End-Interview'),
 ('3. UU 27/2022, JDIH Kemkomdigi', 'https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/undangundang%20nomor%2027%20tahun%202022'),
 ('4. Repository baseline', 'https://github.com/rakamindev/ai-interview-platform/tree/b836d02'),
]
for label, url in refs:
    add(f'<a href="{escape(url,quote=True)}" color="#075f68">{escape(label)}</a>', 'SmallText')
add('The user-supplied fullstack brief is the task source. Assumptions and local execution evidence are identified separately throughout this report. The report does not claim legal certification, user research or measured hiring impact.', 'SmallText')

file = OUT / 'Submission_Report.pdf'
doc = SimpleDocTemplate(str(file), pagesize=A4, rightMargin=48, leftMargin=48, topMargin=57, bottomMargin=60, title='Evidence before a decision / Product Engineer Case Study', author='AI-assisted case study implementation')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(file)
