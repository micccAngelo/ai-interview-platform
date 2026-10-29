import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import PortfolioPage from '../src/pages/portfolio/PortfolioPage';
import SkillPortfolioCard from '../src/components/portfolio/SkillPortfolioCard';
import ComparisonTable from '../src/components/fitgap/ComparisonTable';
import { sessionsApi } from '../src/services/sessions';
import { vacanciesApi } from '../src/services/vacancies';
import { portfoliosApi } from '../src/services/portfolios';
import { portfolio } from './fixtures';

vi.mock('../src/services/sessions', () => ({ sessionsApi: { getPortfolio: vi.fn(), get: vi.fn(), regeneratePortfolio: vi.fn() } }));
vi.mock('../src/services/vacancies', () => ({ vacanciesApi: { list: vi.fn() } }));
vi.mock('../src/services/portfolios', () => ({ portfoliosApi: { getOverride: vi.fn(), exportPortfolio: vi.fn() } }));
function mount() {
  return render(<MemoryRouter initialEntries={['/assessments/1/sessions/1/portfolio']}><Routes>
    <Route path="/assessments/:id/sessions/:sessionId/portfolio" element={<PortfolioPage />} />
  </Routes></MemoryRouter>);
}
beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(sessionsApi.getPortfolio).mockResolvedValue({ data: { portfolio: structuredClone(portfolio) } } as never);
  vi.mocked(sessionsApi.get).mockResolvedValue({ data: { session: { candidate_name: 'Synthetic demo candidate' } } } as never);
  vi.mocked(vacanciesApi.list).mockResolvedValue({ data: { vacancies: [{ id: 1, role_title: 'Frontend Engineer' }] } } as never);
});
describe('evidence review workflow', () => {
  it('separates assessed and missing evidence without inventing a low score', async () => {
    mount();
    expect(await screen.findByText(/1 skill.*follow-up/)).toBeInTheDocument();
    expect(screen.getByText('Not assessed')).toBeInTheDocument();
    expect(screen.getByText('This skill was not explored in the interview.')).toBeInTheDocument();
    expect(screen.getByText(portfolio.skills[0].evidence[0])).toBeInTheDocument();
    expect(screen.getAllByText('Review or override rating')).toHaveLength(1);
  });
  it('filters follow-up work and restores the complete view', async () => {
    const user = userEvent.setup(); mount(); await screen.findByText('Database Design & SQL');
    await user.click(screen.getByRole('button', { name: 'Follow-up (1)' }));
    expect(screen.queryByText('React / Frontend Development')).not.toBeInTheDocument();
    expect(screen.getByText('Database Design & SQL')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'All (2)' }));
    expect(screen.getByText('React / Frontend Development')).toBeInTheDocument();
  });
  it('exposes a network failure and supports retry', async () => {
    vi.mocked(sessionsApi.getPortfolio).mockRejectedValueOnce(new Error('offline'));
    const user = userEvent.setup(); mount();
    expect(await screen.findByRole('alert')).toHaveTextContent('could not load');
    await user.click(screen.getByRole('button', { name: 'Retry loading' }));
    expect(await screen.findByText('Database Design & SQL')).toBeInTheDocument();
  });
  it('shows loading while the request is pending', () => {
    vi.mocked(sessionsApi.getPortfolio).mockReturnValue(new Promise(() => {})); mount();
    expect(screen.getByRole('status')).toHaveTextContent('Loading candidate evidence');
  });
  it('distinguishes pending generation from an empty result', async () => {
    vi.mocked(sessionsApi.getPortfolio).mockResolvedValue({ data: { status: 'generating' } } as never); mount();
    expect(await screen.findByText('Checking the interview evidence')).toBeInTheDocument();
    expect(screen.queryByText('No skills to review yet')).not.toBeInTheDocument();
  });
  it('retries failed generation through the real session client', async () => {
    vi.mocked(sessionsApi.getPortfolio).mockResolvedValue({ data: { portfolio: { ...portfolio, generation_status: 'failed' } } } as never);
    vi.mocked(sessionsApi.regeneratePortfolio).mockResolvedValue({ data: {} } as never);
    const user = userEvent.setup(); mount();
    await user.click(await screen.findByRole('button', { name: 'Retry generation' }));
    await waitFor(() => expect(sessionsApi.regeneratePortfolio).toHaveBeenCalledWith(1));
  });
  it('provides an actionable empty state', async () => {
    vi.mocked(sessionsApi.getPortfolio).mockResolvedValue({ data: { portfolio: { ...portfolio, skills: [] } } } as never); mount();
    expect(await screen.findByText('No skills to review yet')).toBeInTheDocument();
  });
  it('does not present legacy ratings as verified', () => {
    render(<SkillPortfolioCard skill={{ ...portfolio.skills[0], assessment_status: 'legacy' }} onOverrideSaved={vi.fn()} />);
    expect(screen.getByText('Legacy rating: evidence not verified')).toBeInTheDocument();
    expect(screen.queryByText('Review or override rating')).not.toBeInTheDocument();
  });
  it('requires rationale and preserves notes after a failed override save', async () => {
    vi.mocked(portfoliosApi.getOverride).mockRejectedValueOnce(new Error('offline'));
    const user = userEvent.setup(); render(<SkillPortfolioCard skill={portfolio.skills[0]} onOverrideSaved={vi.fn()} />);
    await user.click(screen.getByText('Review or override rating'));
    expect(screen.getByRole('button', { name: 'Save reviewer override' })).toBeDisabled();
    await user.type(screen.getByLabelText(/Reason for this rating/), 'The candidate explained a measured trade-off.');
    await user.selectOptions(screen.getByLabelText('Reviewer level'), '4');
    await user.click(screen.getByRole('button', { name: 'Save reviewer override' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('not saved');
    expect(screen.getByLabelText(/Reason for this rating/)).toHaveValue('The candidate explained a measured trade-off.');
    expect(portfoliosApi.getOverride).toHaveBeenCalledWith(1, { override_level: 4, assessor_notes: 'The candidate explained a measured trade-off.' });
  });
  it('reads expected_level from the API and keeps null unassessed', () => {
    render(<ComparisonTable comparisons={[{ skill_label: 'SQL', expected_level: 4, candidate_level: null, delta: null, result: 'not_assessed' }]} />);
    expect(screen.getByText('L4')).toBeInTheDocument();
    expect(screen.getByText('Unassessed')).toBeInTheDocument();
    expect(screen.queryByText('L1')).not.toBeInTheDocument();
  });
  it('renders long model text literally', () => {
    const quote = '<img src=x onerror=alert(1)>' + 'candidate evidence '.repeat(160);
    const { container } = render(<SkillPortfolioCard skill={{ ...portfolio.skills[0], evidence: [quote] }} onOverrideSaved={vi.fn()} />);
    expect(container.querySelector('blockquote')?.textContent).toBe(quote);
    expect(container.querySelector('img')).toBeNull();
  });
});
