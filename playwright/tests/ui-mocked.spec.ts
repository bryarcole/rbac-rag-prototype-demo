import { test, expect } from '@playwright/test';

/**
 * Deterministic UI tests with a mocked `/query` LLM endpoint.
 * Runs in < 3 seconds with $0 AWS Bedrock spend.
 */
test.describe('RAG UI — Mocked Deterministic Tests', () => {
  test('renders chat response and opens citation drawer on click', async ({ page }) => {
    await page.route('**/query', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          answer: 'Page the on-call SRE via PagerDuty within 5 minutes [DOC-ENG-01].',
          citations: [
            {
              doc_id: 'DOC-ENG-01',
              title: 'Production Incident Runbook (SEV-1)',
              similarity_score: 0.892,
              snippet: 'For SEV-1 production outages, page the on-call SRE via PagerDuty within 5 minutes.',
            },
          ],
          retrieved_contexts: ['For SEV-1 production outages, page the on-call SRE via PagerDuty within 5 minutes.'],
          user_role: 'engineering',
          status: 'answered',
          latency_ms: 412,
          input_tokens: 180,
          output_tokens: 24,
          estimated_cost_usd: 0.000114,
        }),
      });
    });

    await page.goto('/');
    await page.getByTestId('role-select').selectOption('engineering');
    await page.getByTestId('question-input').fill('What is the SEV-1 outage procedure?');
    await page.getByTestId('submit-btn').click();

    await expect(page.getByTestId('chat-response')).toBeVisible();
    await expect(page.getByTestId('answer-text')).toContainText('PagerDuty');
    await expect(page.getByTestId('response-meta')).toContainText('Latency: 412ms');

    // Click citation pill and verify source inspection drawer
    await page.getByTestId('citation-btn-DOC-ENG-01').click();
    await expect(page.getByTestId('citation-drawer')).toBeVisible();
    await expect(page.getByTestId('drawer-title')).toContainText('Production Incident Runbook (SEV-1)');
    await expect(page.getByTestId('drawer-snippet')).toContainText('PagerDuty within 5 minutes');
  });

  test('renders graceful error banner when backend returns HTTP 500', async ({ page }) => {
    await page.route('**/query', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Bedrock throttled request' }),
      });
    });

    await page.goto('/');
    await page.getByTestId('question-input').fill('Trigger error state');
    await page.getByTestId('submit-btn').click();

    await expect(page.getByTestId('error-banner')).toBeVisible();
    await expect(page.getByTestId('error-banner')).toContainText('Request failed (500)');
    await expect(page.getByTestId('chat-response')).toBeHidden();
  });

  test('renders graceful error banner on HTTP 403 unauthorized role', async ({ page }) => {
    await page.route('**/query', async (route) => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid role' }),
      });
    });

    await page.goto('/');
    await page.getByTestId('question-input').fill('Unauthorized check');
    await page.getByTestId('submit-btn').click();

    await expect(page.getByTestId('error-banner')).toBeVisible();
    await expect(page.getByTestId('error-banner')).toContainText('403');
  });
});
