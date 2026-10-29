import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const demo = JSON.parse(await fs.readFile('../api/tmp/evidence-demo.json', 'utf8'));
const browser = await chromium.launch({ channel: 'chrome', headless: true });
try {
  const context = await browser.newContext();
  await context.addInitScript(token => localStorage.setItem('auth_token', token), demo.token);
  const page = await context.newPage();
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const review = 'http://127.0.0.1:5173' + demo.path;
  async function download(name, output) {
    const pending = page.waitForEvent('download'); await page.getByRole('button', { name, exact: true }).click();
    const file = await pending; await file.saveAs('../assessment/private/' + output);
    assert.equal((await fs.readFile('../assessment/private/' + output)).subarray(0,4).toString(), '%PDF');
    console.log('PASS:', name, 'downloads a valid PDF');
  }
  await page.goto(review); await page.getByText('Database Design & SQL', { exact: true }).waitFor();
  await download('Export PDF', 'browser-portfolio.pdf');
  await page.getByLabel('Role to compare').selectOption(String(demo.vacancy_id));
  await page.getByRole('button', { name: 'Compare with role', exact: true }).click();
  await page.getByRole('heading', { name: 'Compare evidence, fairly.' }).waitFor();
  await download('Export comparison PDF', 'browser-comparison.pdf');
  await page.getByRole('link', { name: 'Evidence review', exact: true }).click();
  await page.getByRole('navigation', { name: 'Assessment breadcrumb' }).getByRole('link', { name: 'Assessment sessions', exact: true }).click();
  await page.waitForURL('**/invite'); console.log('PASS: Assessment sessions breadcrumb opens the existing session page');
  await page.goto(review);
  await page.getByRole('navigation', { name: 'Assessment breadcrumb' }).getByRole('link', { name: 'Assessments', exact: true }).click();
  await page.waitForURL('**/assessments'); console.log('PASS: Assessments breadcrumb opens assessment list');
  await page.getByRole('banner').getByRole('link', { name: 'Vacancies', exact: true }).click();
  await page.waitForURL('**/vacancies'); console.log('PASS: Vacancies navigation opens vacancy list');
  await page.getByRole('banner').getByRole('link', { name: 'Assessments', exact: true }).click();
  await page.waitForURL('**/assessments');
  await page.getByRole('link', { name: 'Rakamin AI Interview', exact: true }).click();
  console.log('PASS: Assessments navigation and existing brand link open assessment list');
  await page.route(url => url.pathname === '/api/v1/vacancies', route => route.fulfill({ json: { vacancies: [] } }), { times: 1 });
  await page.goto(review); await page.getByRole('link', { name: 'Create a vacancy', exact: true }).click();
  await page.waitForURL('**/vacancies/new'); console.log('PASS: Empty-role action opens existing vacancy creation page (no vacancy submitted)');
  await page.getByRole('button', { name: 'Logout', exact: true }).click();
  await page.waitForURL('**/login'); assert.equal(await page.evaluate(() => localStorage.getItem('auth_token')), null);
  console.log('PASS: Logout clears browser token and opens login');
  assert.deepEqual(errors, []); console.log('PASS: No browser page errors in the recorded navigation/export checks');
  await context.close();
} finally { await browser.close(); }
