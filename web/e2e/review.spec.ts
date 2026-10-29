import { test, expect, type Page } from '@playwright/test';
import { portfolio } from '../tests/fixtures';
const route = '/assessments/1/sessions/1/portfolio';
const shots = '../assessment/screenshots/';
async function fixtureApi(page: Page) {
  const state = { portfolio: structuredClone(portfolio), failed: false, savingFails: true, loading: false };
  await page.addInitScript(() => localStorage.setItem('auth_token', 'synthetic-browser-test-only'));
  await page.route('**/api/v1/**', async (request) => {
    const url = new URL(request.request().url());
    const path = url.pathname;
    const send = (json: unknown, status = 200) => request.fulfill({ status, json });
    if (path.endsWith('/portfolio/regenerate')) { state.portfolio.generation_status = 'complete'; return send({ portfolio: state.portfolio }); }
    if (path.endsWith('/portfolio')) {
      if (state.loading) await new Promise((resolve) => setTimeout(resolve, 1500));
      if (state.failed) return send({ errors: [{ message: 'Synthetic connection error' }] }, 503);
      return send({ portfolio: state.portfolio });
    }
    if (path.endsWith('/sessions/1')) return send({ session: { id: 1, candidate_name: 'Synthetic demo candidate', status: 'ended' }, assessment: { name: 'Frontend Engineer' } });
    if (path.endsWith('/vacancies')) return send({ vacancies: [{ id: 1, role_title: 'Frontend Engineer / synthetic role' }] });
    if (path.endsWith('/override')) {
      if (state.savingFails) return send({ errors: [{ message: 'Synthetic save failure' }] }, 503);
      const input = request.request().postDataJSON().override;
      const override = { ...input, id: 1, portfolio_skill_id: 1, ai_level: 3, overridden_by: 9001 };
      state.portfolio.overrides = [override]; return send({ override });
    }
    if (path.endsWith('/fitgap/1')) return send({ report: { id: 1, portfolio_id: 1, vacancy_id: 1,
      skill_comparisons: [{ skill_label: 'React / Frontend Development', expected_level: 3, candidate_level: state.portfolio.overrides[0]?.override_level ?? 3, delta: 0, result: 'match', confidence: 'high', is_override: !!state.portfolio.overrides.length },
        { skill_label: 'Database Design & SQL', expected_level: 4, candidate_level: null, delta: null, result: 'not_assessed' }],
      overall_narrative: '1 of 2 requirements have assessed evidence. 1 needs follow-up. Skill comparisons support human review.', culture_narrative: null } });
    if (path.endsWith('/export')) return url.searchParams.get('format') === 'json' ? send({ portfolio: state.portfolio }) : send({ errors: [{ message: 'Synthetic export failure' }] }, 503);
    if (path.endsWith('/transcript')) return send({ turns: [{ id: 1, turn_number: 1, speaker: 'candidate', text: portfolio.skills[0].evidence[0], created_at: '2026-10-29T00:00:00Z' }], total: 1 });
    return send({});
  });
  return state;
}
async function noOverflow(page: Page) {
  if (!(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))) {
    console.log(await page.evaluate(() => Array.from(document.querySelectorAll('*')).filter((element) => element.getBoundingClientRect().right > innerWidth + 1).map((element) => ({ tag: element.tagName, cls: element.className, right: element.getBoundingClientRect().right })).slice(0, 12)));
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
}
test('review, override failure/recovery, comparison, export and transcript', async ({ page }) => {
  const state = await fixtureApi(page);
  const errors: string[] = []; page.on('pageerror', (error) => errors.push(error.message));
  await page.goto(route); await expect(page.getByText('Database Design & SQL')).toBeVisible();
  await page.screenshot({ path: shots + '01-review-desktop.png', fullPage: true });
  await page.getByText('Candidate evidence (1)').click(); await page.getByText('Candidate evidence (1)').click();
  await page.getByText('Review or override rating').click();
  await page.getByLabel('Reviewer level').selectOption('4');
  await page.getByLabel(/Reason for this rating/).fill('Synthetic reviewer rationale: assessed the trade-off in transcript context.');
  await page.getByRole('button', { name: 'Save reviewer override' }).click();
  await expect(page.getByRole('alert')).toContainText('not saved');
  await page.getByRole('alert').screenshot({ path: shots + '02b-save-error-message.png' });
  await page.screenshot({ path: shots + '02-override-save-error.png', fullPage: true });
  state.savingFails = false; await page.getByRole('button', { name: 'Save reviewer override' }).click();
  await expect(page.getByText('Saved reviewer rationale')).toBeVisible();
  await page.getByLabel(/Reason for this rating/).focus(); await page.keyboard.press('Escape');
  await expect(page.getByLabel(/Reason for this rating/)).not.toBeVisible();
  await page.getByRole('button', { name: 'Follow-up (1)' }).click();
  await expect(page.getByText('React / Frontend Development')).toHaveCount(0);
  await page.getByRole('button', { name: 'All (2)' }).click();
  await page.getByLabel('Role to compare').selectOption('1');
  await page.getByRole('button', { name: 'Compare with role' }).click();
  await expect(page.getByText('L4', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('Unassessed', { exact: true })).toBeVisible();
  await page.screenshot({ path: shots + '03-role-comparison.png', fullPage: true });
  await page.getByRole('button', { name: 'Export comparison PDF' }).click();
  await expect(page.getByRole('alert')).toContainText('could not be downloaded');
  await page.getByRole('button', { name: 'Retry comparison' }).click();
  await page.getByRole('link', { name: 'Evidence review', exact: true }).click();
  const download = page.waitForEvent('download'); await page.getByRole('button', { name: 'Export JSON' }).click();
  expect((await download).suggestedFilename()).toBe('portfolio-1.json');
  await page.getByRole('link', { name: 'Read transcript' }).click();
  await expect(page.getByText(portfolio.skills[0].evidence[0])).toBeVisible();
  expect(errors).toEqual([]);
});
test('network retry, empty, pending and failed generation states', async ({ page }) => {
  const state = await fixtureApi(page); state.failed = true;
  await page.goto(route); await expect(page.getByRole('alert')).toBeVisible();
  await page.screenshot({ path: shots + '04-request-error.png', fullPage: true });
  state.failed = false; await page.getByRole('button', { name: 'Retry loading' }).click();
  await expect(page.getByText('Database Design & SQL')).toBeVisible();
  state.portfolio.skills = []; await page.reload(); await expect(page.getByText('No skills to review yet')).toBeVisible();
  await page.screenshot({ path: shots + '05-empty.png', fullPage: true });
  state.portfolio.generation_status = 'pending'; await page.reload(); await expect(page.getByText('Checking the interview evidence')).toBeVisible();
  await page.getByRole('button', { name: 'Check status' }).click();
  await page.screenshot({ path: shots + '06-generating.png', fullPage: true });
  state.portfolio.generation_status = 'failed'; await page.reload(); await expect(page.getByText('Generation needs another attempt')).toBeVisible();
  await page.screenshot({ path: shots + '07-generation-failed.png', fullPage: true });
  await page.getByRole('button', { name: 'Retry generation' }).click(); await expect(page.getByText('No skills to review yet')).toBeVisible();
});
test('mobile, long text, keyboard focus and 200 percent text resize', async ({ page }) => {
  const state = await fixtureApi(page);
  await page.setViewportSize({ width: 390, height: 844 }); await page.goto(route);
  await expect(page.getByText('Database Design & SQL')).toBeVisible(); await noOverflow(page);
  await page.screenshot({ path: shots + '08-review-mobile.png', fullPage: true });
  await page.screenshot({ path: shots + '08b-mobile-overview.png' });
  await page.locator('.review-skill').first().evaluate((element) => element.scrollIntoView({ block: 'start' }));
  await page.screenshot({ path: shots + '08c-mobile-evidence.png' });
  state.portfolio.skills[0].evidence = ['Synthetic long-text fixture: ' + 'very-long-unbroken-evidence'.repeat(90)];
  await page.reload(); await expect(page.getByText('Database Design & SQL')).toBeVisible(); await noOverflow(page);
  await page.keyboard.press('Tab');
  expect(await page.evaluate(() => {
    const style = getComputedStyle(document.activeElement!); return parseFloat(style.outlineWidth) >= 2 || style.boxShadow !== 'none';
  })).toBe(true);
  await page.addStyleTag({ content: 'html { font-size: 200%; }' });
  await page.screenshot({ path: shots + '09-mobile-text-200.png', fullPage: true });
  await noOverflow(page);
});
