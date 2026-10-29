from pathlib import Path
import json, re, subprocess
ROOT = Path(__file__).resolve().parents[1]
A = ROOT/'assessment'
def read(name):
    return re.sub(r'\x1b\[[0-9;]*m', '', (A/name).read_text(encoding='utf-8-sig'))
backend = re.findall(r'(\d+) examples?, (\d+) failures?', read('backend-tests.log'))[-1]
assert int(backend[0]) > 0 and int(backend[1]) == 0
frontend = int(re.findall(r'Tests\s+(\d+) passed', read('frontend-tests.log'))[-1])
browser = int(re.findall(r'(\d+) passed \(', read('browser-tests.log'))[-1])
assert frontend > 0 and browser > 0 and 'built in' in read('frontend-build.log')
assert read('control-check.log').count('PASS:') == 9
assert 'PASS: live Rails API' in read('live-api-smoke.log')
assert '1 example, 1 failure' in read('seeded-fault-red.log')
assert '1 example, 0 failures' in read('seeded-fault-green.log')
contrast = json.loads((A/'contrast-check.json').read_text(encoding='utf-8'))
assert not contrast['failures']
old = json.loads((A/'verification.json').read_text(encoding='utf-8-sig')) if (A/'verification.json').exists() else {}
video = A/'walkthrough.webm'
duration = None
if video.exists():
    details = subprocess.run([str(ROOT/'.runtime/ffmpeg/ffmpeg-win64.exe'), '-hide_banner', '-i', str(video)], capture_output=True, text=True).stderr
    match = re.search(r'Duration: (\d+):(\d+):([\d.]+)', details)
    assert match, details
    duration = int(match[1])*3600 + int(match[2])*60 + float(match[3])
    assert 180 <= duration <= 300, duration
proof = {
    'date': '2026-10-30', 'timezone': 'Asia/Jakarta',
    'branch': 'feat/evidence-first-assessment',
    'source_head': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
    'source_head_description': 'Repository snapshot containing the tested API/web source; later commits may change documentation or packaging only.',
    'publication_choice': 'Keep everything in Rakamin2, per the user instruction. No external publication or portal submission.',
    'baseline': 'b836d02', 'backend_status': 'passed', 'backend_examples': int(backend[0]),
    'frontend_tests': frontend, 'browser_tests': browser, 'production_build': 'passed',
    'live_control_checks': 9,
    'live_api_summary': read('live-api-smoke.log').strip(),
    'contrast_samples': contrast['sampleCount'], 'contrast_pairs': contrast['distinctPairCount'],
    'video_local_status': 'complete' if duration else 'recording', 'video_duration_seconds': duration,
    'ci_status': old.get('ci_status','Configuration supplied; GitHub execution not yet verified.'),
    'pr_url': old.get('pr_url'), 'video_url': old.get('video_url'),
    'seeded_fault': {'branch': 'test/seeded-missing-rating',
        'mutant': 'fbd99f85174bc508ad4b18325176fd73b2ac9829',
        'revert': 'dc5058b2df147f72d351a5491d097e13633d1a31',
        'result': '1 example, 1 expected failure; after revert, 1 example, 0 failures. Assertions unchanged.'},
    'limitations': ['No live Gemini or microphone interview', 'Synthetic fixtures only', 'Docker setup not executed',
        'No fairness calibration or legal compliance certification', 'PDF font coverage beyond Latin not validated']
}
(A/'verification.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
print(json.dumps({key:proof[key] for key in ['backend_examples','frontend_tests','browser_tests','contrast_samples','video_local_status','video_duration_seconds']}))
