import { chromium } from 'playwright';
import fs from 'node:fs/promises';
const demo = JSON.parse(await fs.readFile('../api/tmp/evidence-demo.json', 'utf8'));
const browser = await chromium.launch({ channel: 'chrome' });
const context = await browser.newContext();
await context.addInitScript((token) => localStorage.setItem('auth_token', token), demo.token);
const page = await context.newPage();
async function inspect() {
  return page.evaluate(() => {
    function rgba(value) { const numbers = value.match(/[\d.]+/g)?.map(Number) ?? [0, 0, 0, 0]; return [numbers[0], numbers[1], numbers[2], numbers[3] ?? 1]; }
    function blend(top, bottom) { return top.slice(0, 3).map((channel, index) => channel * top[3] + bottom[index] * (1 - top[3])); }
    function background(element) { const parent = element.parentElement ? background(element.parentElement) : [255, 255, 255]; return blend(rgba(getComputedStyle(element).backgroundColor), parent); }
    function luminance(rgb) { const values = rgb.map((x) => { const channel = x / 255; return channel <= .04045 ? channel / 12.92 : ((channel + .055) / 1.055) ** 2.4; }); return values[0] * .2126 + values[1] * .7152 + values[2] * .0722; }
    return Array.from(document.querySelectorAll('body *')).filter((element) => element.getClientRects().length && !element.closest(':disabled') &&
      (Array.from(element.childNodes).some((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim()) || ['INPUT', 'TEXTAREA', 'SELECT'].includes(element.tagName)))
      .map((element) => {
        const style = getComputedStyle(element); const bg = background(element); const fg = blend(rgba(style.color), bg);
        const a = luminance(bg), b = luminance(fg); const ratio = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
        const large = parseFloat(style.fontSize) >= 24 || (parseFloat(style.fontSize) >= 18.667 && Number(style.fontWeight) >= 700);
        return { text: element.textContent.trim().slice(0, 65), tag: element.tagName, foreground: fg.map(Math.round), background: bg.map(Math.round), ratio: Math.round(ratio * 100) / 100, minimum: large ? 3 : 4.5 };
      });
  });
}
await page.goto('http://127.0.0.1:5173' + demo.path); await page.getByText('Database Design & SQL', { exact: true }).waitFor();
const samples = await inspect();
await page.getByText(/Review or override rating|Edit reviewer override/).first().click();
await page.getByLabel(/Reason for this rating/).first().fill('Synthetic failed-save fixture for contrast verification.');
await page.route('**/api/v1/portfolio_skills/*/override', (route) => route.fulfill({ status: 503, json: { errors: [{ message: 'Synthetic failure' }] } }), { times: 1 });
await page.getByRole('button', { name: 'Save reviewer override' }).first().click(); await page.getByRole('alert').waitFor();
samples.push(...await inspect());
await page.getByLabel('Role to compare').selectOption(String(demo.vacancy_id)); await page.getByRole('button', { name: 'Compare with role' }).click();
await page.getByRole('heading', { name: 'Compare evidence, fairly.' }).waitFor(); samples.push(...await inspect());
const failures = samples.filter((sample) => sample.ratio < sample.minimum);
const pairs = [...new Set(samples.map((sample) => JSON.stringify([sample.foreground, sample.background])))];
await fs.writeFile('../assessment/contrast-check.json', JSON.stringify({ scope: 'Visible text and form controls in real API evidence review, failed override, and role comparison; disabled controls excluded', sampleCount: samples.length, distinctPairCount: pairs.length, minimumRatio: Math.min(...samples.map((sample) => sample.ratio)), failures, samples }, null, 2));
await browser.close();
if (failures.length) { console.error(JSON.stringify(failures, null, 2)); process.exitCode = 1; }
else console.log(`PASS: ${samples.length} visible text/control samples across ${pairs.length} foreground/background pairs meet their AA text thresholds.`);
