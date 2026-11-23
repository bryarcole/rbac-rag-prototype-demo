import { test, expect } from '@playwright/test';

/**
 * 2 Live End-to-End Smoke Tests hitting real Amazon Bedrock.
 * Enabled when RUN_LIVE_SMOKE=1 is set (e.g., in CI with AWS creds).
 */
test.describe('Live Bedrock E2E Smoke Tests', () => {
  test.skip(process.env.RUN_LIVE_SMOKE !== '1', 'Set RUN_LIVE_SMOKE=1 to run live Bedrock smoke tests');

  test('Smoke 1: Engineering role retrieves SEV-1 runbook with valid schema', async ({ request }) => {
    const res = await request.post('/query', {
      headers: { 'X-User-Role': 'engineering' },
      data: { question: 'What are the immediate steps for a SEV-1 outage?' },
    });
    expect(res.status()).toBe(200);
    const data = await res.json();
    expect(data.status).toBe('answered');
    expect(data.answer).toContain('PagerDuty');
    expect(typeof data.latency_ms).toBe('number');
    expect(typeof data.estimated_cost_usd).toBe('number');
    expect(data.citations.length).toBeGreaterThan(0);
  });

  test('Smoke 2: Engineering role is blocked from HR salary bands in UI', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('role-select').selectOption('engineering');
    await page.getByTestId('question-input').fill('What is the base salary band for an L5 Senior Engineer?');
    await page.getByTestId('submit-btn').click();

    await expect(page.getByTestId('chat-response')).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId('answer-text')).not.toContainText('175,000');
  });
});
