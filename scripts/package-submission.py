from pathlib import Path
import hashlib
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

assert not git('status', '--porcelain'), 'Commit the final source and artifacts before packaging.'
assert git('branch', '--show-current') == 'feat/evidence-first-assessment'
commit = git('rev-parse', 'HEAD')
bundle = ROOT/'assessment/evidence-first.bundle'
archive = ROOT/'Rakamin2-submission.zip'
subprocess.run(['git', 'bundle', 'create', str(bundle), '--branches', '--tags', 'HEAD'], cwd=ROOT, check=True)
subprocess.run(['git', 'bundle', 'verify', str(bundle)], cwd=ROOT, check=True)
subprocess.run(['git', 'archive', '--format=zip', '--prefix=Rakamin2/', '-o', str(archive), 'HEAD'], cwd=ROOT, check=True)
with zipfile.ZipFile(archive, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
    output.write(bundle, 'Rakamin2/assessment/evidence-first.bundle')
    output.writestr('Rakamin2/PACKAGE_COMMIT.txt', f'Branch: feat/evidence-first-assessment\nCommit: {commit}\nPublication: local only, per user instruction\n')
with zipfile.ZipFile(archive) as output:
    assert output.testzip() is None, 'Archive integrity check failed.'
    names = output.namelist()
    for required in ['START_HERE.md', 'assessment/evidence-first.bundle', 'assessment/verification.json',
                     'assessment/design-verification.md', 'api/app/services/portfolios/response_validator.rb',
                     'web/src/pages/portfolio/PortfolioPage.tsx']:
        assert 'Rakamin2/' + required in names, required
    for name in names:
        assert not any(part in name for part in ['/.runtime/', '/node_modules/', '/vendor/bundle/', '/.git/', '/assessment/private/'])
        assert not name.endswith(('.env.local', 'api/tmp/evidence-demo.json'))
    for relative in ['assessment/Submission_Report.pdf', 'assessment/sample-portfolio.pdf', 'assessment/walkthrough.webm']:
        assert output.read('Rakamin2/' + relative) == (ROOT/relative).read_bytes(), f'Artifact bytes changed: {relative}'
print(f'PASS: archive CRC, required files, excluded runtime/secrets, and exact PDF/video bytes ({len(names)} entries).')
print(f'Archive: {archive} ({archive.stat().st_size:,} bytes)')
print(f'SHA256: {hashlib.sha256(archive.read_bytes()).hexdigest()}')
print(f'Git history: {bundle} ({bundle.stat().st_size:,} bytes)')
