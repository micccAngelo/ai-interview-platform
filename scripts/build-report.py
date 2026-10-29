from pathlib import Path
from html import escape
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assessment'
proof = json.loads((OUT / 'verification.json').read_text(encoding='utf-8-sig'))
FONTS = Path('C:/Windows/Fonts')
for family, regular, bold in [
    ('Reading', 'georgia.ttf', 'georgiab.ttf'),
    ('Label', 'calibri.ttf', 'calibrib.ttf'),
    ('Code', 'consola.ttf', 'consolab.ttf'),
]:
    pdfmetrics.registerFont(TTFont(family, str(FONTS / regular)))
    pdfmetrics.registerFont(TTFont(family + 'Bold', str(FONTS / bold)))
    pdfmetrics.registerFontFamily(family, normal=family, bold=family + 'Bold')

INK = colors.HexColor('#263440')
RUST = colors.HexColor('#97482f')
MUTED = colors.HexColor('#505b65')
PAPER = colors.HexColor('#f6f3ef')
LINE = colors.HexColor('#d6d5d2')
WHITE = colors.white
LEFT, RIGHT = 66, 44
W = A4[0] - LEFT - RIGHT
styles = {
    'body': ParagraphStyle('Body', fontName='Reading', fontSize=9.5, leading=15, textColor=INK, spaceAfter=9),
    'small': ParagraphStyle('Small', fontName='Label', fontSize=9, leading=12.5, textColor=MUTED, spaceAfter=7),
    'title': ParagraphStyle('Title', fontName='Reading', fontSize=24, leading=29, textColor=INK, spaceAfter=15),
    'cover': ParagraphStyle('Cover', fontName='Reading', fontSize=31, leading=37, textColor=INK, spaceAfter=18),
    'sub': ParagraphStyle('Sub', fontName='LabelBold', fontSize=11.5, leading=15, textColor=INK, spaceBefore=10, spaceAfter=7),
    'kicker': ParagraphStyle('Kicker', fontName='LabelBold', fontSize=10, leading=14, textColor=RUST, spaceAfter=9),
    'cell': ParagraphStyle('Cell', fontName='Label', fontSize=9, leading=12.3, textColor=INK),
    'cellhead': ParagraphStyle('CellHead', fontName='LabelBold', fontSize=9, leading=12.3, textColor=WHITE),
    'code': ParagraphStyle('Code', fontName='Code', fontSize=8, leading=12, textColor=INK, spaceAfter=6),
    'caption': ParagraphStyle('Caption', fontName='Label', fontSize=8.5, leading=11.5, textColor=MUTED, spaceAfter=10),
}
story = []

def p(text, style='body'):
    return Paragraph(text, styles[style])

def add(text, style='body'):
    story.append(p(text, style))

def title(step, text):
    add(step, 'kicker')
    add(text, 'title')

def sub(text):
    add(text, 'sub')

def table(headers, rows, widths):
    data = [[p(escape(str(value)), 'cellhead') for value in headers]]
    data.extend([[p(escape(str(value)), 'cell') for value in row] for row in rows])
    item = Table(data, colWidths=[W * width for width in widths], repeatRows=1, hAlign='LEFT')
    item.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), INK),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, PAPER]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1.4, RUST),
        ('LINEBELOW', (0, 1), (-1, -1), .35, LINE),
    ]))
    story.append(item)
    story.append(Spacer(1, 10))

def note(label, text):
    item = Table([[p(label, 'kicker')], [p(text, 'small')]], colWidths=[W])
    item.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PAPER),
        ('LINEBEFORE', (0, 0), (0, -1), 2, RUST),
        ('LEFTPADDING', (0, 0), (-1, -1), 13),
        ('RIGHTPADDING', (0, 0), (-1, -1), 13),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(item)
    story.append(Spacer(1, 12))

def screenshot(name, max_height=455, width=W):
    image = Image(str(OUT / 'screenshots' / name))
    scale = min(width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    image.hAlign = 'LEFT'
    story.append(image)
    story.append(Spacer(1, 8))

def newpage():
    story.append(PageBreak())

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, A4[1] - 9, A4[0], 9, fill=1, stroke=0)
    canvas.setFont('Label', 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(LEFT, A4[1] - 34, 'AI Interview Platform / Fullstack Product Engineer')
    canvas.setStrokeColor(LINE)
    canvas.line(LEFT, 43, A4[0] - RIGHT, 43)
    canvas.setFont('Label', 8)
    canvas.drawString(LEFT, 29, 'Technical report / 30 October 2026')
    canvas.setFillColor(RUST)
    canvas.setFont('LabelBold', 10)
    canvas.drawRightString(A4[0] - RIGHT, 28, f'{doc.page:02d}')
    if doc.page > 1:
        canvas.setFillColor(RUST)
        canvas.rect(27, A4[1] - 96, 3, 34, fill=1, stroke=0)
        canvas.setFont('LabelBold', 10)
        canvas.drawString(26, A4[1] - 112, f'{doc.page - 1:02d}')
    canvas.restoreState()

add('Rakamin engineering assignment', 'kicker')
story.append(Spacer(1, 14))
add('Missing ratings in<br/>interview portfolios', 'cover')
add('A Rails and React change to preserve unassessed skills through review, role comparison and export.')
story.append(Spacer(1, 9))
table(['Repository', 'Working copy'], [
    ['rakamindev/ai-interview-platform', 'C:/Rakamin2'],
    ['Baseline', 'main at b836d02'],
    ['Feature branch', 'feat/evidence-first-assessment'],
    ['Work dates', '29-30 October 2026'],
], [.40, .60])
sub('Problem addressed')
add('A missing model rating could become level 1 through numeric coercion. For example, an interview that never assessed SQL could still produce a low SQL score. The revised pipeline stores that skill as not assessed and keeps the same meaning in the assessor screen and exports.')
sub('Local verification')
add(f"{proof['backend_examples']} backend examples, {proof['frontend_tests']} component tests and {proof['browser_tests']} browser workflows passed. TypeScript and the production build passed. A deliberate missing-rating fault failed the existing regression test; reverting it restored the test.")
sub('Report contents')
contents = [
    ('Repository and local setup', '02'), ('Users and assessment policy', '03'),
    ('Findings and priorities', '04'), ('Acceptance criteria', '05'),
    ('Implementation decisions', '06'), ('Tests and corrections', '07'),
    ('Desktop review', '08'), ('Mobile and failed saves', '09'),
    ('Delivery and release notes', '10'),
]
outline = Table([[p(label, 'small'), p(page, 'small')] for label, page in contents],
    colWidths=[W - 30, 30], hAlign='LEFT')
outline.setStyle(TableStyle([
    ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
]))
story.append(outline)
story.append(Spacer(1, 9))
add('Prepared with AI assistance. Demonstration records are synthetic. The source, command logs and technical-defense notes accompany this report.', 'small')

newpage()
title('Step 1 / Setup', 'Repository and local setup')
add('The project runs from C:/Rakamin2. The original main branch remains at b836d02; implementation commits are on feat/evidence-first-assessment. The code review followed assessment setup, interview sessions, portfolio generation, overrides, vacancy comparison and export.')
table(['Layer', 'Environment and work completed'], [
    ['API', 'Ruby 3.3.2, Rails 7.0 and PostgreSQL. Added RSpec coverage for validation, persistence, requests and background work.'],
    ['Web', 'React 18, TypeScript, Vite, Tailwind and Radix. Added Vitest, Testing Library, Playwright and a dependency lockfile.'],
    ['Local database', 'A dedicated PostgreSQL cluster listens on localhost:54329. Tests check persisted rows, null ratings, rollback and concurrent jobs.'],
    ['Model response', 'A deterministic injected response exercises the real validator and persistence code without calling Gemini.'],
    ['Windows tooling', 'Task-local Ruby and database tools are in the ignored .runtime directory. Dependencies and local credentials are excluded from the source archive.'],
], [.25, .75])
sub('Commands used')
add('API', 'small')
add('bundle exec rails db:prepare<br/>bundle exec rspec --format documentation', 'code')
add('Web', 'small')
add('npm ci<br/>npm test<br/>npm run build<br/>npm run test:e2e', 'code')
sub('What the local run covers')
add('Verification starts with a completed interview and covers portfolio generation, human review, comparison and export. The recording uses the running Rails API and synthetic records. No live Gemini or microphone interview was run. Docker was unavailable; compose configuration is included as an untested alternative.')
add('The brief gives a deadline of Wednesday 19 August, 13:00 WIB. This work was prepared on 29-30 October 2026. Submission availability needs confirmation with the recruiter.', 'small')

newpage()
title('Step 2 / Product context', 'Users and assessment policy')
add('The product specification calls for probing capability and using transcript evidence. Its workflow connects the interview portfolio to reviewer overrides and vacancy comparison. [1, 2] A rating error can therefore reach several screens and exported files.')
add('The user needs below are assumptions drawn from that workflow and the assignment brief. No recruiter or candidate interviews were conducted.', 'small')
table(['User', 'Need reflected in the change'], [
    ['Assessor', 'Read the supporting excerpt in context before accepting or changing a rating. Require a reason for an override.'],
    ['Recruiter', 'See which skills need another assessment before sharing the portfolio. Keep those gaps visible in exports.'],
    ['Hiring manager', 'Compare evidence with actual role requirements. Distinguish a demonstrated skill gap from a requirement the interview missed.'],
    ['Candidate', 'Avoid a low score for a skill that was never assessed. Keep a human reviewer responsible for interpreting the evidence.'],
], [.25, .75])
sub('Handling candidate data in Indonesia')
add('UU 27/2022 includes correction and access rights in Articles 6-7, objections to certain solely automated decisions in Article 10, and impact assessment for high-risk processing in Article 34. It also addresses purpose, accuracy and confidentiality. [3]')
add('The implementation binds evidence access to the authenticated tenant, filters sensitive log fields and avoids exposing raw provider errors. Reviewers can record a reason for changing an assessed rating. These are engineering safeguards; the work does not establish legal compliance.')
note('Policy questions before production', 'The controller still needs to decide legal basis, retention, deletion, candidate correction and objection processes, provider arrangements and any required impact assessment. Language effects and fairness need evaluation with consented data.')

newpage()
title('Step 3 / Code review', 'Findings and priorities')
table(['Priority / type', 'Observed behavior', 'Change or remaining decision'], [
    ['P0 / defect', 'Portfolio and override lookups were not joined through the authenticated tenant.', 'Tenant-scoped lookups and foreign-ID request tests.'],
    ['P0 / policy', 'Password login could select an organization without a user-membership relation.', 'Restrict local login to opt-in development use. Production identity remains an integration requirement.'],
    ['P1 / defect', 'Numeric coercion and clamping converted missing or malformed ratings to valid-looking levels.', 'Validate types; store invalid or missing ratings as not assessed.'],
    ['P1 / defect', 'Generation deleted old skill rows before validating all replacements.', 'Validate first, then replace rows and completion status in one transaction.'],
    ['P1 / defect', 'Duplicate or exhausted jobs could regenerate or mark completed work as failed.', 'Serialize by session, skip completed work and guard exhaustion updates.'],
    ['P1 / undefined', 'Quote provenance, unassessed states and confidence limits had no clear rules.', 'Define acceptance criteria and implement a response validator.'],
    ['P1 / inference', 'The comparison prompt requested culture fit and hiring advice from score patterns.', 'Use deterministic skill comparison; remove those inferences.'],
    ['P2 / contract', 'The API sent expected_level while the UI read required_level.', 'Use the API field consistently and test the contract.'],
    ['P2 / interface', 'Request errors were swallowed. Long text and enlarged text broke parts of the mobile layout.', 'Add retry feedback and fix the layouts caught by browser tests.'],
    ['P3 / setup', 'Setup examples used inconsistent API ports and frontend folder names.', 'Correct the defaults and add a runbook.'],
], [.16, .49, .35])
add('P0 covers candidate-data access; P1 covers misleading results or evidence loss; P2 covers interpretation and recovery; P3 covers setup. These priorities reflect expected impact, not measured incident rates.', 'small')

newpage()
title('Step 4 / Definition of done', 'Acceptance criteria')
add('These criteria were committed before implementation. The full list and trade-offs are in assessment/acceptance-criteria.md.', 'small')
table(['Boundary', 'Required behavior'], [
    ['Rating type', 'Accept only integer levels 1-5. Reject null, strings, floats, booleans and out-of-range values as ratings.'],
    ['Coverage', 'Return every configured skill. Omitted or untouched skills remain explicitly unassessed.'],
    ['Evidence', 'Require 1-3 bounded excerpts found in candidate turns after whitespace normalization. Interviewer-only or invented quotes cannot support a rating.'],
    ['Confidence', 'Accept known confidence values and cap them by interview coverage and probe count. Confidence describes the signal, not candidate ability.'],
    ['Response shape', 'Unknown or duplicate identities and malformed JSON fail the attempt without replacing existing rows.'],
    ['Publication', 'Commit all replacement rows and completion status together. Validation or database failure restores the previous rows.'],
    ['Jobs', 'Serialize duplicate jobs and skip completed work. A queue failure stays retryable; an older exhausted job cannot overwrite completion.'],
    ['Historical data', 'Mark old ratings as legacy without changing their levels or claiming verified provenance. Refuse rollback that would require inventing levels.'],
    ['Override', 'Allow overrides only for assessed rows. Require a reason and retain the original AI level, reviewer and timestamp.'],
    ['Authorization', 'Return 404 for foreign-tenant resources. Candidate roles cannot read assessor evidence. Background comparison checks both tenants.'],
    ['Role comparison', 'Use expected_level. Different canonical IDs cannot match by label; ambiguous custom matches remain unassessed.'],
    ['Interface', 'Cover loading, empty, error, partial, legacy and long-text states, keyboard focus, 390px layout and 200% text resizing.'],
], [.25, .75])

newpage()
title('Step 4 / Approach', 'Implementation decisions')
table(['Option', 'Effect', 'Trade-off'], [
    ['UI warning only', 'Helps a reviewer notice missing evidence.', 'Leaves coerced scores and destructive replacement behavior in the API and export. Rejected.'],
    ['Validation and atomic writes', 'Chosen. Checks evidence before publishing a complete set of skill rows.', 'Requires a schema change and holds a database connection and session lock during the bounded model call.'],
    ['Versioned ledger and outbox', 'Adds review history and more durable job scheduling.', 'Needs more migrations and operational work. Kept as a follow-up to the immediate rating fix.'],
], [.22, .38, .40])
sub('Data path')
table(['Interview', 'Validation', 'Publication', 'Review', 'Comparison'], [[
    'Ended session and transcript', 'Types, coverage and candidate quotes', 'Skill rows and status in one transaction',
    'Evidence and attributed override', 'Role requirements and export',
]], [.2, .2, .2, .2, .2])
sub('Schema and rollback')
add('The migration adds assessment_status and assessment_reason, and makes ai_level nullable. A database check requires a null level for not_assessed and a level for assessed or legacy. Existing scores retain their values and receive legacy status.')
add('Tests round-trip legacy rows through the migration. The down migration refuses to run while null ratings exist. An application rollback can retain the additive schema; a schema rollback first needs a decision about those unassessed records.')
sub('Timeouts and retries')
add('The portfolio call has a 180-second HTTP read timeout and no nested provider retries. Sidekiq handles durable retries. The timeout is not an end-to-end deadline, and the session lock does not guarantee exactly-once provider billing.')
add('Quote matching is deliberately conservative: a paraphrase can be rejected. It checks where a quote came from; a reviewer must still judge whether the quote supports the rating.', 'small')

newpage()
title('Step 5 / Verification', 'Tests and corrections')
table(['Check', 'Recorded result'], [
    ['Backend', f"{proof['backend_examples']} examples passed against PostgreSQL, covering validation, tenant requests, rollback, jobs and concurrent duplicates."],
    ['Frontend', f"{proof['frontend_tests']} component tests and {proof['browser_tests']} browser workflows passed. TypeScript and the Vite production build passed."],
    ['Real API', 'Four skills returned: two assessed, two null. SQL stayed unassessed with expected_level=4. JSON and PDF exports passed.'],
    ['Browser controls', f"{proof['live_control_checks']} live checks passed for PDF downloads, navigation, empty-role action and logout, with no page errors."],
], [.24, .76])
sub('Deliberate regression')
add('On test/seeded-missing-rating, the missing-rating result was deliberately changed from null to level 1. The existing regression test failed. Reverting the change restored the test without changing its assertion.')
fault = proof['seeded_fault']
add(f"Fault: {escape(fault['mutant'])}<br/>Revert: {escape(fault['revert'])}", 'code')
add(escape(fault['result']), 'small')
sub('Corrections during verification')
add('The first AI-generated savepoint implementation still saved an extra skill row after rollback. Rails retained the rolled-back association target and autosaved it when recording failure. Reloading the portfolio before that update cleared the cached target. The original failing output is in ai-verification-red.log; the assertion stayed unchanged.')
add('TypeScript also caught a nonexistent regeneration method and an incorrect assumption that a union response always contained a portfolio. Browser checks caught squeezed skill headings on phones and navigation overflow at 200% text size. Those checks passed after correcting the code and layout.')
add('These results cover synthetic fixtures and an injected model response. They do not validate live Gemini quality, audio interviews, model calibration or hiring fairness.', 'small')

newpage()
title('Step 5 / Screenshots', 'Desktop review')
add('The review shows coverage before individual skill ratings. This capture uses a synthetic browser fixture with one assessed skill and one skill requiring follow-up.', 'small')
screenshot('01-review-desktop.png', 450)
add('Figure 1. The fixture API supplies the counts and statuses. The SQL row has no score; its follow-up action remains visible.', 'caption')
sub('Review order')
add('Each assessed row puts the summary and candidate excerpt above the override form. Reviewers can open the transcript before changing a rating. The role selector sits alongside the evidence so a comparison is available from the same workspace.')
add('The application retains the repository\'s teal and yellow styling. Native disclosure controls keep long excerpts manageable. The contrast check sampled 177 visible text and control combinations across review, failed save and comparison, with no AA text-threshold failures. Disabled controls were excluded.', 'small')

newpage()
title('Step 5 / Screenshots', 'Mobile and failed saves')
add('Browser tests exercise the review at 390px, with long unbroken text and with text enlarged to 200%. They check for horizontal page overflow.', 'small')
phone_images = []
for name in ['08b-mobile-overview.png', '08c-mobile-evidence.png']:
    image = Image(str(OUT / 'screenshots' / name))
    scale = min((W * .45) / image.imageWidth, 420 / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    phone_images.append(image)
phones = Table([phone_images], colWidths=[W * .5, W * .5], hAlign='LEFT')
phones.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
]))
story.append(phones)
story.append(Spacer(1, 8))
add('Figure 2. Phone overview and evidence detail. Full-resolution captures are included in assessment/screenshots/.', 'caption')
sub('Failed override save')
screenshot('02b-save-error-message.png', 48)
add('Figure 3. The test deliberately fails a save. The form keeps the reviewer\'s reason, reports that it was not saved and allows another attempt. The retry succeeds.', 'caption')
add('Separate browser checks cover request retry, empty results, pending generation and failed generation. The recording labels its simulated failures and then shows recovery through the real API.', 'small')

newpage()
title('Delivery', 'Delivery and release notes')
table(['Artifact', 'Contents'], [
    ['api/ and web/', 'Implementation and tests on feat/evidence-first-assessment.'],
    ['assessment/', 'Command logs, verification.json, screenshots and sample exports.'],
    ['walkthrough.webm', f"Captioned local recording, {proof['video_duration_seconds']:.0f} seconds. No narration."],
    ['Supporting notes', 'RUNBOOK.md, technical-defense.md and a prepared PR_DESCRIPTION.md.'],
    ['Portable package', 'Rakamin2-submission.zip includes source and artifacts. evidence-first.bundle preserves the project branches and fault/revert history.'],
], [.29, .71])
sub('Submission links')
for label, key in [('Pull request', 'pr_url'), ('Walkthrough', 'video_url')]:
    url = proof.get(key)
    if url:
        add(f'{label}: <a href="{escape(url, quote=True)}" color="#97482f">{escape(url)}</a>', 'small')
    else:
        add(f'{label}: not published; the local material is included in the package.', 'small')
add('Before submitting, publish the prepared PR, host the recording and add both links here. No portal submission has been made.' if not proof.get('pr_url') and not proof.get('video_url') else 'Check that both links are accessible to the recruiter before uploading this PDF. Portal submission is not recorded.', 'small')
sub('Release sequence and remaining work')
add('Apply the additive migration, then deploy the API and web together so both understand nullable ratings. Review legacy portfolios and arrange follow-up assessments. Monitor failed generation, pending-job age, provider latency, missing evidence and overrides.')
add('The implementation keeps only the latest override. An append-only review ledger, durable outbox and abandoned-job watchdog remain follow-ups. Production also depends on trusted organization identity and the controller\'s privacy policies. PDF font coverage beyond Latin is unverified.', 'small')
sub('Sources')
refs = [
    ('1. Product behavior specification', 'https://github.com/rakamindev/ai-interview-platform/wiki/PRD-01-%E2%80%94-First-Principles:-AI-Interview-Behavior'),
    ('2. Product workflow simulation', 'https://github.com/rakamindev/ai-interview-platform/wiki/PRD-02-%E2%80%94-Real-Simulation:-End%E2%80%90to%E2%80%90End-Interview'),
    ('3. UU 27/2022, JDIH Kemkomdigi', 'https://jdih.komdigi.go.id/produk_hukum/view/id/832/t/undangundang%20nomor%2027%20tahun%202022'),
    ('4. Repository baseline b836d02', 'https://github.com/rakamindev/ai-interview-platform/tree/b836d02'),
]
for label, url in refs:
    add(f'<a href="{escape(url, quote=True)}" color="#97482f">{escape(label)}</a>', 'small')

file = OUT / 'Submission_Report.pdf'
doc = SimpleDocTemplate(str(file), pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT,
    topMargin=65, bottomMargin=59, title='Missing ratings in interview portfolios',
    author='AI-assisted case study implementation')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(file)
